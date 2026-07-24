"""Independent OPC UA history recording for master-recipe executions.

The recorder intentionally owns its OPC UA clients, event loop and writer
thread.  It does not share connections or mutable state with ``control.py``.
"""

from __future__ import annotations

import asyncio
import csv
import inspect
import os
import re
import shutil
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from defusedxml import ElementTree

try:  # Keep catalog/CSV tests usable in environments without asyncua.
    from asyncua import Client
except ImportError:  # pragma: no cover - exercised through a monkeypatched client
    Client = None  # type: ignore[assignment]


_MISSING = "Missing"
_NO_COMMUNICATION = "BadNoCommunication"
_READABLE_ACCESS = {"1", "3"}
_UNREADABLE_ACCESS = {"0", "2"}
_CSV_DELIMITER = ";"
_CSV_SCHEMA_VERSION = "2"


@dataclass
class SignalDescriptor:
    """A single deduplicated OPC UA value selected from an executed procedure."""

    endpoint: str
    namespace: str
    node_address: str
    module_name: str
    signal_type: str
    signal_name: str
    channel: str
    unit: str = ""
    access: str | None = None
    procedure_ids: set[str] = field(default_factory=set)
    procedure_numbers: set[str] = field(default_factory=set)
    step_ids: set[str] = field(default_factory=set)
    signal_id: str = ""

    @property
    def key(self) -> tuple[str, str, str]:
        return self.endpoint, self.namespace, self.node_address

    @property
    def group_key(self) -> tuple[str, str, str]:
        return self.endpoint, self.namespace, self.module_name

    @property
    def column_name(self) -> str:
        procedures = "+".join(sorted(self.procedure_ids)) or "unknown-procedure"
        parts = (
            self.module_name,
            procedures,
            self.signal_type,
            self.signal_name,
            self.channel,
            self.unit or "-",
        )
        return "__".join(_column_part(part) for part in parts)


@dataclass(frozen=True)
class CacheEntry:
    value: Any
    quality: str
    source_timestamp: datetime | None = None
    server_timestamp: datetime | None = None
    quality_detail: str | None = None


@dataclass(frozen=True)
class ProcedureParameterRecord:
    step_id: str
    module_name: str
    procedure_id: str
    procedure_number: str
    procedure_name: str
    parameter_id: str
    parameter_name: str
    configured_value: Any
    unit: str


@dataclass(frozen=True)
class RecordingResult:
    output_path: Path
    snapshot_count: int
    status: str
    signal_count: int


@dataclass
class _Connection:
    client: Any
    subscription: Any
    nodes: list[Any]
    signals: list[SignalDescriptor]


class _SubscriptionHandler:
    def __init__(self, manager: "OpcUaRecordingManager", group_key: tuple[str, str, str]):
        self.manager = manager
        self.group_key = group_key

    def datachange_notification(self, node: Any, value: Any, data: Any) -> None:
        if (
            self.manager._stopped
            or self.group_key in self.manager._unavailable_groups
        ):
            return
        signal_key = self.manager._node_to_signal.get(
            (self.group_key, _node_id_text(node))
        )
        if signal_key is None:
            return
        data_value = getattr(getattr(data, "monitored_item", None), "Value", None)
        if data_value is None:
            entry = CacheEntry(value=value, quality="Good")
        else:
            parsed_value, quality, source_ts, server_ts = _parse_data_value(data_value)
            entry = CacheEntry(
                value=value if parsed_value is None else parsed_value,
                quality=quality,
                source_timestamp=source_ts,
                server_timestamp=server_ts,
            )
        self.manager._update_cache(signal_key, entry)

    def status_change_notification(self, status: Any) -> None:
        if self.manager._stopped:
            return
        status_code = getattr(status, "Status", status)
        text = _status_text(status_code)
        is_good = getattr(status_code, "is_good", None)
        try:
            good = bool(is_good()) if callable(is_good) else text.lower().startswith("good")
        except Exception:
            good = text.lower().startswith("good")
        if not good:
            self.manager._warn(
                f"Module '{self.group_key[2]}' subscription status changed to {text}"
            )
            self.manager._mark_group_unavailable(self.group_key)


class OpcUaRecordingManager:
    """Record the values belonging to procedures selected for one recipe run."""

    def __init__(
        self,
        procedure: Iterable[Any],
        recipe_files: Iterable[str | os.PathLike[str]] | None,
        logger: Callable[[str], None] | None,
        sampling_interval_s: float = 1.0,
        output_path: str | os.PathLike[str] | None = None,
    ) -> None:
        if sampling_interval_s <= 0:
            raise ValueError("sampling_interval_s must be greater than zero")

        self.procedure = list(procedure or [])
        self.recipe_files = [Path(path) for path in (recipe_files or [])]
        self.logger = logger
        self.sampling_interval_s = float(sampling_interval_s)
        self.output_path = (
            Path(output_path)
            if output_path is not None
            else Path(__file__).resolve().parents[2]
            / "artifacts"
            / "dataHistory"
            / "lastRecord.csv"
        )

        self.signals: list[SignalDescriptor] = []
        self.procedure_parameters: list[ProcedureParameterRecord] = []
        self.executable_step_count = 0
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None

        self._cache: dict[tuple[str, str, str], CacheEntry] = {}
        self._cache_lock = threading.Lock()
        self._connections: dict[tuple[str, str, str], _Connection] = {}
        self._node_to_signal: dict[
            tuple[tuple[str, str, str], str], tuple[str, str, str]
        ] = {}
        self._unavailable_groups: set[tuple[str, str, str]] = set()
        self._warnings: list[str] = []
        self._active_group_count = 0

        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_stop: asyncio.Event | None = None
        self._run_task: asyncio.Task[Any] | None = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._started = False
        self._stopped = False
        self._spool_path: Path | None = None
        self._spool_file: Any = None
        self._spool_writer: csv.writer | None = None
        self._spool_lock = threading.Lock()
        self._snapshot_count = 0
        self._had_quality_issues = False
        self._thread_error: BaseException | None = None
        self._reconnect_interval_s = 5.0
        self._shutdown_timeout_s = 15.0
        self._forced_shutdown_timeout_s = 2.0

    def start(self) -> None:
        """Build the catalog, subscribe all selected modules, and start sampling."""
        if self._started:
            raise RuntimeError("Recording manager has already been started")
        self._started = True
        self.started_at = _utc_now()
        self._log(
            f"[HIST] Recording requested (sampling interval: "
            f"{self.sampling_interval_s:g} s)."
        )

        self.signals, self.executable_step_count = self._build_signal_catalog()
        self.procedure_parameters = self._build_procedure_parameters()
        self._log(
            f"[HIST] Selected {len(self.signals)} unique signal(s) from "
            f"{self.executable_step_count} executable procedure step(s)."
        )
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._open_spool()

        if not self.signals:
            self._warn("No readable procedure signals were selected")
            self._ready.set()
            self._log(f"[HIST] Recording started: {self.output_path}.")
            return
        if Client is None:
            self._warn("asyncua is not installed")
            self._ready.set()
            self._log(f"[HIST] Recording started: {self.output_path}.")
            return

        self._thread = threading.Thread(
            target=self._thread_main,
            name="OpcUaRecordingManager",
            daemon=True,
        )
        self._thread.start()
        # A recipe must not start before subscriptions and initial reads were
        # attempted, otherwise its first state/parameter changes may be lost.
        if not self._ready.wait(timeout=30.0):
            self._warn("Timed out while preparing OPC UA subscriptions")
        if self._thread_error is not None:
            raise RuntimeError(
                f"Recorder startup failed: {type(self._thread_error).__name__}: "
                f"{self._thread_error}"
            ) from self._thread_error
        self._log(f"[HIST] Recording started: {self.output_path}.")

    def stop(
        self, recipe_status: str, error: BaseException | str | None = None
    ) -> RecordingResult:
        """Stop all clients and atomically publish the final CSV file."""
        if self._stopped:
            return self._result(recipe_status, error)
        self._stopped = True
        self.ended_at = _utc_now()

        self._request_async_shutdown(force=False)
        thread_alive = False
        if self._thread is not None:
            self._thread.join(timeout=self._shutdown_timeout_s)
            if self._thread.is_alive():
                self._warn(
                    "Recorder thread did not terminate after the graceful "
                    "shutdown request"
                )
                self._request_async_shutdown(force=True)
                self._thread.join(timeout=self._forced_shutdown_timeout_s)
            thread_alive = self._thread.is_alive()
            if thread_alive:
                timeout_error = TimeoutError(
                    "Recorder thread did not terminate after forced cancellation"
                )
                if self._thread_error is None:
                    self._thread_error = timeout_error
                self._warn(str(timeout_error))

        spool_closed = self._close_spool(timeout_s=1.0 if thread_alive else None)
        if not spool_closed:
            if self._thread_error is None:
                self._thread_error = TimeoutError(
                    "Recorder spool remained busy during shutdown"
                )
            self._warn(
                "Recorder spool remained busy; CSV finalization was skipped"
            )
        if self._thread_error is not None:
            self._warn(
                f"{type(self._thread_error).__name__}: {self._thread_error}"
            )

        status = self._recording_status(recipe_status, error)
        if spool_closed:
            try:
                self._finalize_csv(recipe_status, status, error)
            except Exception as exc:
                status = "failed"
                self._warn(f"Could not finalize CSV: {type(exc).__name__}: {exc}")
        else:
            status = "failed"
        result = RecordingResult(
            output_path=self.output_path,
            snapshot_count=self._snapshot_count,
            status=status,
            signal_count=len(self.signals),
        )
        self._log(
            f"[HIST] Recording stopped: {self.output_path} "
            f"({self._snapshot_count} snapshots, status={status})."
        )
        return result

    def _request_async_shutdown(self, force: bool) -> None:
        loop = self._loop
        stop_event = self._async_stop
        run_task = self._run_task
        if loop is None:
            return

        def request() -> None:
            if stop_event is not None:
                stop_event.set()
            if force and run_task is not None and not run_task.done():
                run_task.cancel()

        try:
            loop.call_soon_threadsafe(request)
        except RuntimeError:
            pass

    def _iter_executable_steps(self) -> Iterable[tuple[str, dict[str, Any]]]:
        position = 0
        occurrences: dict[str, int] = {}
        for step in self.procedure:
            if not isinstance(step, dict):
                continue
            if step.get("mtp") is None or step.get("inst") is None:
                continue
            position += 1
            base_step_id = _step_identifier(step, position)
            occurrence = occurrences.get(base_step_id, 0) + 1
            occurrences[base_step_id] = occurrence
            step_id = base_step_id if occurrence == 1 else f"{base_step_id}#{occurrence}"
            yield step_id, step

    def _build_procedure_parameters(self) -> list[ProcedureParameterRecord]:
        records: list[ProcedureParameterRecord] = []
        for step_id, step in self._iter_executable_steps():
            mtp = step["mtp"]
            instance = step["inst"]
            module_name = _module_name(mtp)
            procedure_id = _procedure_id(instance)
            procedure_number = _procedure_number(instance)
            procedure_name = str(
                getattr(instance, "name", "") or procedure_id
            )

            for configured in list(step.get("params") or []):
                if not isinstance(configured, (list, tuple)) or len(configured) < 2:
                    continue
                parameter, value = configured[0], configured[1]
                parameter_id = str(
                    getattr(parameter, "id", "") or "unknown-parameter"
                )
                parameter_name = str(
                    getattr(parameter, "name", "") or parameter_id
                )
                records.append(
                    ProcedureParameterRecord(
                        step_id=step_id,
                        module_name=module_name,
                        procedure_id=procedure_id,
                        procedure_number=procedure_number,
                        procedure_name=procedure_name,
                        parameter_id=parameter_id,
                        parameter_name=parameter_name,
                        configured_value=value,
                        unit=_configured_parameter_unit(step, parameter),
                    )
                )
        return records

    def _build_signal_catalog(
        self,
    ) -> tuple[list[SignalDescriptor], int]:
        deduplicated: dict[tuple[str, str, str], SignalDescriptor] = {}
        step_count = 0
        for step_id, step in self._iter_executable_steps():
            mtp = step.get("mtp")
            instance = step.get("inst")
            # Nested lists (parallel groups), transitions, init/end and unmapped
            # steps are excluded by _iter_executable_steps().
            step_count += 1
            endpoint = str(getattr(mtp, "url", "") or "")
            namespace = str(getattr(mtp, "ns", "") or "")
            module_name = _module_name(mtp)
            procedure_id = _procedure_id(instance)
            procedure_number = _procedure_number(instance)

            for parameter in list(getattr(instance, "params", None) or []):
                signal_type = _normalise_parameter_type(parameter)
                channel = _channel_for(parameter, signal_type)
                if channel is None:
                    continue
                channel_data = (getattr(parameter, "paramElem", None) or {}).get(channel)
                if not isinstance(channel_data, dict):
                    continue
                node_address = channel_data.get("ID")
                if node_address is None or str(node_address).strip() == "":
                    self._warn(
                        f"Parameter '{getattr(parameter, 'name', '?')}' has no "
                        f"node ID for channel {channel}; skipped"
                    )
                    continue
                access_raw = channel_data.get("Access")
                access = None if access_raw is None else str(access_raw).strip()
                if access in _UNREADABLE_ACCESS:
                    self._warn(
                        f"Node '{node_address}' is not readable (Access={access}); skipped"
                    )
                    continue
                if access not in _READABLE_ACCESS:
                    self._warn(
                        f"Node '{node_address}' has no known Access value; "
                        "subscription will be attempted"
                    )

                descriptor = SignalDescriptor(
                    endpoint=endpoint,
                    namespace=namespace,
                    node_address=str(node_address),
                    module_name=module_name,
                    signal_type=signal_type,
                    signal_name=str(getattr(parameter, "name", "") or getattr(
                        parameter, "id", "unknown-signal"
                    )),
                    channel=channel,
                    unit=str(getattr(parameter, "unit", "") or ""),
                    access=access,
                    procedure_ids={procedure_id},
                    procedure_numbers={procedure_number} if procedure_number else set(),
                    step_ids={step_id},
                )
                existing = deduplicated.get(descriptor.key)
                if existing is None:
                    deduplicated[descriptor.key] = descriptor
                else:
                    _merge_signal_descriptors(existing, descriptor)

        signals = sorted(
            deduplicated.values(),
            key=lambda signal: (
                signal.module_name,
                signal.endpoint,
                signal.namespace,
                signal.node_address,
                signal.signal_type,
                signal.signal_name,
            ),
        )
        for index, signal in enumerate(signals, start=1):
            signal.signal_id = f"S{index:03d}"
        return signals, step_count

    def _thread_main(self) -> None:
        try:
            asyncio.run(self._run())
        except asyncio.CancelledError as exc:
            if not self._stopped:
                self._thread_error = exc
        except BaseException as exc:  # preserve diagnostics without killing recipe
            self._thread_error = exc
        finally:
            self._ready.set()

    async def _run(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._run_task = asyncio.current_task()
        self._async_stop = asyncio.Event()
        groups: dict[tuple[str, str, str], list[SignalDescriptor]] = {}
        for signal in self.signals:
            groups.setdefault(signal.group_key, []).append(signal)

        sampler: asyncio.Task[Any] | None = None
        reconnector: asyncio.Task[Any] | None = None
        stop_waiter: asyncio.Task[Any] | None = None
        try:
            await asyncio.gather(
                *(self._connect_group(key, group) for key, group in groups.items())
            )
            self._active_group_count = len(self._connections)

            # Persist the initial cache before start() releases the recipe thread.
            self._record_snapshot()
            self._ready.set()

            sampler = asyncio.create_task(
                self._sample_loop(), name="opcua-recording-sampler"
            )
            reconnector = asyncio.create_task(
                self._reconnect_loop(groups), name="opcua-recording-reconnector"
            )
            stop_waiter = asyncio.create_task(
                self._async_stop.wait(), name="opcua-recording-stop"
            )
            done, _pending = await asyncio.wait(
                {sampler, reconnector, stop_waiter},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for completed_task in done:
                if completed_task is stop_waiter:
                    continue
                if completed_task.cancelled():
                    if not self._async_stop.is_set():
                        raise RuntimeError(
                            f"{completed_task.get_name()} was cancelled unexpectedly"
                        )
                    continue
                task_error = completed_task.exception()
                if task_error is not None:
                    raise task_error
                if not self._async_stop.is_set():
                    raise RuntimeError(
                        f"{completed_task.get_name()} stopped unexpectedly"
                    )
        finally:
            self._ready.set()
            background_tasks = [
                task
                for task in (sampler, reconnector, stop_waiter)
                if task is not None
            ]
            for task in background_tasks:
                if not task.done():
                    task.cancel()
            if background_tasks:
                await asyncio.gather(*background_tasks, return_exceptions=True)
            await asyncio.gather(
                *(self._disconnect_group(key) for key in list(self._connections)),
                return_exceptions=True,
            )
            self._run_task = None

    async def _connect_group(
        self,
        group_key: tuple[str, str, str],
        signals: list[SignalDescriptor],
    ) -> bool:
        endpoint, namespace, module_name = group_key
        client = None
        subscription = None
        node_mapping_keys: list[tuple[tuple[str, str, str], str]] = []
        try:
            client = Client(url=endpoint)
            await client.connect()
            namespace_index = await client.get_namespace_index(uri=namespace)
            nodes = [
                client.get_node(f"ns={namespace_index};s={signal.node_address}")
                for signal in signals
            ]
            handler = _SubscriptionHandler(self, group_key)
            subscription = await client.create_subscription(
                self.sampling_interval_s * 1000.0, handler
            )
            for node, signal in zip(nodes, signals):
                mapping_key = (group_key, _node_id_text(node))
                self._node_to_signal[mapping_key] = signal.key
                node_mapping_keys.append(mapping_key)

            subscribe_results = await subscription.subscribe_data_change(
                nodes, sampling_interval=self.sampling_interval_s * 1000.0
            )
            if not isinstance(subscribe_results, (list, tuple)):
                subscribe_results = [subscribe_results]

            successful_nodes: list[Any] = []
            successful_signals: list[SignalDescriptor] = []
            for index, (node, signal) in enumerate(zip(nodes, signals)):
                result = (
                    subscribe_results[index]
                    if index < len(subscribe_results)
                    else None
                )
                if result is None or _subscription_result_failed(result):
                    mapping_key = (group_key, _node_id_text(node))
                    self._node_to_signal.pop(mapping_key, None)
                    detail = (
                        "missing subscription result"
                        if result is None
                        else _status_text(result)
                    )
                    self._update_cache(
                        signal.key,
                        CacheEntry(None, _MISSING, quality_detail=detail),
                    )
                    self._warn(
                        f"Module '{module_name}' node '{signal.node_address}' "
                        f"subscription failed: {detail}"
                    )
                    continue
                successful_nodes.append(node)
                successful_signals.append(signal)

            if not successful_nodes:
                self._mark_group_unavailable(group_key)
                self._log(
                    f"[HIST] Module '{module_name}': subscribed 0 signal(s)."
                )
                await _disconnect_client(client, subscription)
                return False

            self._connections[group_key] = _Connection(
                client=client,
                subscription=subscription,
                nodes=successful_nodes,
                signals=successful_signals,
            )
            self._active_group_count = max(self._active_group_count, len(self._connections))
            self._unavailable_groups.discard(group_key)
            await asyncio.gather(
                *(
                    self._initial_read(node, signal)
                    for node, signal in zip(successful_nodes, successful_signals)
                )
            )
            self._log(
                f"[HIST] Module '{module_name}': subscribed "
                f"{len(successful_signals)} signal(s)."
            )
            return True
        except asyncio.CancelledError:
            for mapping_key in node_mapping_keys:
                self._node_to_signal.pop(mapping_key, None)
            if client is not None and group_key not in self._connections:
                await _disconnect_client(client, subscription)
            raise
        except Exception as exc:
            for mapping_key in node_mapping_keys:
                self._node_to_signal.pop(mapping_key, None)
            self._mark_group_unavailable(group_key)
            self._warn(
                f"Module '{module_name}' subscription failed: "
                f"{type(exc).__name__}: {exc}"
            )
            if client is not None:
                await _disconnect_client(client, subscription)
            return False

    async def _initial_read(self, node: Any, signal: SignalDescriptor) -> None:
        try:
            data_value = await node.read_data_value()
            value, quality, source_ts, server_ts = _parse_data_value(data_value)
            self._update_cache(
                signal.key,
                CacheEntry(value, quality, source_ts, server_ts),
            )
        except Exception as exc:
            self._update_cache(
                signal.key,
                CacheEntry(
                    None,
                    _MISSING,
                    quality_detail=f"{type(exc).__name__}: {exc}",
                ),
            )

    async def _disconnect_group(self, group_key: tuple[str, str, str]) -> None:
        connection = self._connections.pop(group_key, None)
        if connection is None:
            return
        for node in connection.nodes:
            self._node_to_signal.pop((group_key, _node_id_text(node)), None)
        await _disconnect_client(connection.client, connection.subscription)

    async def _sample_loop(self) -> None:
        assert self._async_stop is not None
        loop = asyncio.get_running_loop()
        next_sample = loop.time() + self.sampling_interval_s
        while not self._async_stop.is_set():
            delay = max(0.0, next_sample - loop.time())
            try:
                await asyncio.wait_for(self._async_stop.wait(), timeout=delay)
                return
            except asyncio.TimeoutError:
                self._record_snapshot()
                next_sample += self.sampling_interval_s
                if next_sample < loop.time():
                    next_sample = loop.time() + self.sampling_interval_s

    async def _reconnect_loop(
        self,
        groups: dict[tuple[str, str, str], list[SignalDescriptor]],
    ) -> None:
        assert self._async_stop is not None
        while not self._async_stop.is_set():
            try:
                await asyncio.wait_for(
                    self._async_stop.wait(), timeout=self._reconnect_interval_s
                )
                return
            except asyncio.TimeoutError:
                pass

            for group_key, signals in groups.items():
                connection = self._connections.get(group_key)
                healthy = False
                if connection is not None:
                    if group_key in self._unavailable_groups:
                        await self._disconnect_group(group_key)
                        connection = None
                    else:
                        try:
                            check = getattr(connection.client, "check_connection", None)
                            if check is None:
                                healthy = True
                            else:
                                result = check()
                                if inspect.isawaitable(result):
                                    await result
                                healthy = True
                        except Exception:
                            await self._disconnect_group(group_key)
                if not healthy:
                    self._mark_group_unavailable(group_key)
                    await self._connect_group(group_key, signals)

    def _record_snapshot(self, timestamp: datetime | None = None) -> None:
        with self._cache_lock:
            cache = dict(self._cache)
        row: list[Any] = [_iso(timestamp or _utc_now())]
        quality_issues: list[str] = []
        self._ensure_signal_ids()
        for signal in self.signals:
            entry = cache.get(signal.key, CacheEntry(None, _MISSING))
            row.append(_csv_value(entry.value))
            issue = _quality_issue(signal.signal_id, entry)
            if issue:
                quality_issues.append(issue)
        row.append(",".join(quality_issues))
        with self._spool_lock:
            if self._spool_writer is None or self._spool_file is None:
                return
            self._spool_writer.writerow(row)
            if quality_issues:
                self._had_quality_issues = True
            self._spool_file.flush()
            self._snapshot_count += 1

    def _update_cache(
        self, key: tuple[str, str, str], entry: CacheEntry
    ) -> None:
        with self._cache_lock:
            self._cache[key] = entry

    def _mark_group_unavailable(
        self,
        group_key: tuple[str, str, str],
        quality: str = _NO_COMMUNICATION,
    ) -> None:
        self._unavailable_groups.add(group_key)
        keys = [signal.key for signal in self.signals if signal.group_key == group_key]
        with self._cache_lock:
            for key in keys:
                previous = self._cache.get(key)
                self._cache[key] = CacheEntry(
                    None if previous is None else previous.value,
                    quality or _NO_COMMUNICATION,
                    None if previous is None else previous.source_timestamp,
                    None if previous is None else previous.server_timestamp,
                )

    def _open_spool(self) -> None:
        self._ensure_signal_ids()
        handle, name = tempfile.mkstemp(
            prefix=".lastRecord.",
            suffix=".rows.tmp",
            dir=self.output_path.parent,
            text=True,
        )
        os.close(handle)
        self._spool_path = Path(name)
        with self._spool_lock:
            self._spool_file = self._spool_path.open(
                "w", encoding="utf-8", newline=""
            )
            self._spool_writer = csv.writer(
                self._spool_file, delimiter=_CSV_DELIMITER
            )
            self._spool_writer.writerow(self._history_header())
            self._spool_file.flush()

    def _close_spool(self, timeout_s: float | None = None) -> bool:
        if timeout_s is None:
            acquired = self._spool_lock.acquire()
        else:
            acquired = self._spool_lock.acquire(timeout=timeout_s)
        if not acquired:
            return False
        try:
            if self._spool_file is not None and not self._spool_file.closed:
                self._spool_file.flush()
                self._spool_file.close()
            self._spool_writer = None
            self._spool_file = None
            return True
        finally:
            self._spool_lock.release()

    def _ensure_signal_ids(self) -> None:
        for index, signal in enumerate(self.signals, start=1):
            signal.signal_id = f"S{index:03d}"

    def _history_header(self) -> list[str]:
        self._ensure_signal_ids()
        return [
            "timestamp_utc",
            *(signal.signal_id for signal in self.signals),
            "quality_issues",
        ]

    def _procedure_parameter_rows(self) -> list[tuple[Any, ...]]:
        return [
            (
                record.step_id,
                record.module_name,
                record.procedure_id,
                record.procedure_number,
                record.procedure_name,
                record.parameter_id,
                record.parameter_name,
                _csv_value(record.configured_value),
                record.unit,
            )
            for record in self.procedure_parameters
        ]

    def _signal_catalog_rows(self) -> list[tuple[str, ...]]:
        self._ensure_signal_ids()
        return [
            (
                signal.signal_id,
                signal.module_name,
                ",".join(sorted(signal.step_ids)),
                ",".join(sorted(signal.procedure_ids)),
                ",".join(sorted(signal.procedure_numbers)),
                signal.signal_type,
                signal.signal_name,
                signal.channel,
                signal.unit,
                signal.endpoint,
                signal.namespace,
                signal.node_address,
                signal.access or "",
            )
            for signal in self.signals
        ]

    def _finalize_csv(
        self,
        recipe_status: str,
        recording_status: str,
        error: BaseException | str | None,
    ) -> None:
        metadata = self._metadata(recipe_status, recording_status, error)
        fd, temp_name = tempfile.mkstemp(
            prefix=".lastRecord.",
            suffix=".tmp",
            dir=self.output_path.parent,
            text=True,
        )
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            with temp_path.open("w", encoding="utf-8", newline="") as target:
                writer = csv.writer(target, delimiter=_CSV_DELIMITER)
                writer.writerow(("[metadata]",))
                writer.writerow(("key", "value"))
                for key, value in metadata:
                    writer.writerow((key, value))
                writer.writerow(())

                writer.writerow(("[procedure_parameters]",))
                writer.writerow(
                    (
                        "step_id",
                        "module",
                        "procedure_id",
                        "procedure_number",
                        "procedure_name",
                        "parameter_id",
                        "parameter_name",
                        "configured_value",
                        "unit",
                    )
                )
                writer.writerows(self._procedure_parameter_rows())
                writer.writerow(())

                writer.writerow(("[signals]",))
                writer.writerow(
                    (
                        "signal_id",
                        "module",
                        "step_ids",
                        "procedure_ids",
                        "procedure_numbers",
                        "signal_type",
                        "signal_name",
                        "channel",
                        "unit",
                        "endpoint",
                        "namespace",
                        "node_id",
                        "access",
                    )
                )
                writer.writerows(self._signal_catalog_rows())
                writer.writerow(())

                writer.writerow(("[history]",))
                if self._spool_path is not None and self._spool_path.exists():
                    with self._spool_path.open("r", encoding="utf-8", newline="") as source:
                        shutil.copyfileobj(source, target)
                else:
                    writer.writerow(self._history_header())
                target.flush()
                os.fsync(target.fileno())
            os.replace(temp_path, self.output_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
            if self._spool_path is not None and self._spool_path.exists():
                self._spool_path.unlink()

    def _metadata(
        self,
        recipe_status: str,
        recording_status: str,
        error: BaseException | str | None,
    ) -> list[tuple[str, str]]:
        recipe_meta = _recipe_metadata(self.recipe_files)
        module_names = {signal.module_name for signal in self.signals}
        module_names.update(
            _module_name(step["mtp"]) for _step_id, step in self._iter_executable_steps()
        )
        modules = sorted(module_names)
        rows = [
            ("csv_schema_version", _CSV_SCHEMA_VERSION),
            ("recipe_id", recipe_meta["recipe_id"]),
            ("recipe_version", recipe_meta["recipe_version"]),
            ("product_id", recipe_meta["product_id"]),
            (
                "recipe_files",
                ";".join(path.name for path in self.recipe_files),
            ),
            ("recording_started_utc", _iso(self.started_at)),
            ("recording_ended_utc", _iso(self.ended_at)),
            ("recipe_status", str(recipe_status)),
            ("recording_status", recording_status),
            ("sampling_interval_s", f"{self.sampling_interval_s:g}"),
            ("modules", ";".join(modules)),
        ]
        if error is not None:
            rows.append(("error", f"{type(error).__name__}: {error}" if isinstance(
                error, BaseException
            ) else str(error)))
        return rows

    def _recording_status(
        self, recipe_status: str, error: BaseException | str | None
    ) -> str:
        if not self.signals or self._thread_error is not None:
            return "failed"
        if self._active_group_count == 0:
            return "failed"
        if (
            str(recipe_status).lower() != "completed"
            or error is not None
            or self._warnings
            or self._had_quality_issues
            or self._unavailable_groups
        ):
            return "partial"
        return "completed"

    def _result(
        self, recipe_status: str, error: BaseException | str | None
    ) -> RecordingResult:
        return RecordingResult(
            self.output_path,
            self._snapshot_count,
            self._recording_status(recipe_status, error),
            len(self.signals),
        )

    def _warn(self, message: str) -> None:
        self._warnings.append(message)
        self._log(f"[HIST] Warning: {message}; recipe execution continues.")

    def _log(self, message: str) -> None:
        if self.logger is not None:
            try:
                self.logger(message)
                return
            except Exception:
                pass
        print(message)


async def _disconnect_client(client: Any, subscription: Any) -> None:
    try:
        delete = getattr(subscription, "delete", None)
        if delete is not None:
            result = delete()
            if inspect.isawaitable(result):
                await result
    except Exception:
        pass
    try:
        await client.disconnect()
    except Exception:
        pass


def _subscription_result_failed(result: Any) -> bool:
    is_good = getattr(result, "is_good", None)
    if not callable(is_good):
        return False
    try:
        return not bool(is_good())
    except Exception:
        return True


_SIGNAL_METADATA_FIELDS = (
    "module_name",
    "signal_type",
    "signal_name",
    "channel",
    "unit",
    "access",
)


def _signal_metadata_key(signal: SignalDescriptor) -> tuple[str, ...]:
    return tuple(
        str(getattr(signal, attribute) or "")
        for attribute in _SIGNAL_METADATA_FIELDS
    )


def _merge_signal_descriptors(
    existing: SignalDescriptor, candidate: SignalDescriptor
) -> None:
    if _signal_metadata_key(candidate) < _signal_metadata_key(existing):
        for attribute in _SIGNAL_METADATA_FIELDS:
            setattr(existing, attribute, getattr(candidate, attribute))
    existing.procedure_ids.update(candidate.procedure_ids)
    existing.procedure_numbers.update(candidate.procedure_numbers)
    existing.step_ids.update(candidate.step_ids)


def _step_identifier(step: dict[str, Any], position: int) -> str:
    bml = step.get("bml")
    raw = ""
    for attribute in ("getId", "getName"):
        candidate = getattr(bml, attribute, None)
        try:
            value = candidate() if callable(candidate) else candidate
        except Exception:
            value = None
        if value not in (None, ""):
            raw = str(value).strip()
            break
    if not raw:
        raw = str(getattr(bml, "id", "") or "").strip()
    prefix = raw.split(":", 1)[0].strip()
    return prefix or f"{position:03d}"


def _module_name(mtp: Any) -> str:
    return str(
        getattr(mtp, "name", "")
        or Path(str(getattr(mtp, "source_file", "") or "unknown-module")).stem
    )


def _procedure_id(instance: Any) -> str:
    return str(
        getattr(instance, "id", None)
        or getattr(instance, "name", None)
        or getattr(instance, "procId", "unknown-procedure")
    )


def _procedure_number(instance: Any) -> str:
    value = getattr(instance, "procId", None)
    return "" if value is None else str(value)


def _configured_parameter_unit(step: dict[str, Any], parameter: Any) -> str:
    parameter_id = str(getattr(parameter, "id", "") or "")
    bml = step.get("bml")
    get_parameters = getattr(bml, "getParameter", None)
    try:
        recipe_parameters = (
            list(get_parameters() or [])
            if callable(get_parameters)
            else list(getattr(bml, "params", None) or [])
        )
    except Exception:
        recipe_parameters = list(getattr(bml, "params", None) or [])

    for recipe_parameter in recipe_parameters:
        recipe_parameter_id = str(
            getattr(recipe_parameter, "id", "") or ""
        ).rsplit(":", 1)[-1]
        if recipe_parameter_id != parameter_id:
            continue
        unit = str(getattr(recipe_parameter, "unit", "") or "")
        if unit:
            return unit
    return str(getattr(parameter, "unit", "") or "")


def _normalise_parameter_type(parameter: Any) -> str:
    raw = str(
        getattr(parameter, "parameter_type", None)
        or getattr(parameter, "ref_base_system_unit_path", None)
        or ""
    )
    tail = raw.rstrip("/").rsplit("/", 1)[-1].lower()
    if "processvalueout" in tail:
        return "ProcessValueOut"
    if "procedureparameter" in tail:
        return "ProcedureParameter"
    if "processvaluein" in tail:
        return "ProcessValueIn"
    return tail or "Unknown"


def _channel_for(parameter: Any, signal_type: str) -> str | None:
    elements = getattr(parameter, "paramElem", None) or {}
    if signal_type == "ProcessValueOut":
        text = elements.get("Text")
        if isinstance(text, dict) and text.get("ID") not in (None, ""):
            return "Text"
        return "V"
    if signal_type == "ProcedureParameter":
        return "VOut"
    if signal_type == "ProcessValueIn":
        return "V"
    return None


def _parse_data_value(
    data_value: Any,
) -> tuple[Any, str, datetime | None, datetime | None]:
    wrapped = getattr(data_value, "Value", data_value)
    value = getattr(wrapped, "Value", wrapped)
    status = getattr(data_value, "StatusCode", None)
    source_ts = getattr(data_value, "SourceTimestamp", None)
    server_ts = getattr(data_value, "ServerTimestamp", None)
    return value, _status_text(status), source_ts, server_ts


def _status_text(status: Any) -> str:
    if status is None:
        return _MISSING
    name = getattr(status, "name", None)
    if name:
        return str(name)
    text = str(status)
    match = re.search(r"\(([^)]+)\)", text)
    return match.group(1) if match else text


def _node_id_text(node: Any) -> str:
    node_id = getattr(node, "nodeid", node)
    to_string = getattr(node_id, "to_string", None)
    return str(to_string()) if callable(to_string) else str(node_id)


def _column_part(value: Any) -> str:
    text = str(value).strip()
    return re.sub(r"[\r\n;|]+", "_", text) or "-"


def _quality_issue(signal_id: str, entry: CacheEntry) -> str:
    quality = str(entry.quality or _MISSING).strip() or _MISSING
    if quality.lower().startswith("good"):
        return ""
    detail = re.sub(
        r"[\s,=()]+", "_", str(entry.quality_detail or "").strip()
    ).strip("_")
    if detail and detail.lower() != quality.lower():
        return f"{signal_id}={quality}({detail})"
    return f"{signal_id}={quality}"


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, bytes):
        return value.hex()
    return value


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _recipe_metadata(recipe_files: list[Path]) -> dict[str, str]:
    result = {"recipe_id": "", "recipe_version": "", "product_id": ""}
    values: dict[str, list[str]] = {key: [] for key in result}
    for path in recipe_files:
        try:
            root = ElementTree.parse(path).getroot()
        except Exception:
            continue
        recipe_node = next(
            (node for node in root.iter() if _local_name(node.tag) == "MasterRecipe"),
            None,
        )
        if recipe_node is None:
            recipe_node = next(
                (
                    node
                    for node in root.iter()
                    if _local_name(node.tag) == "GeneralRecipe"
                ),
                root,
            )
        recipe_id = _direct_child_text(recipe_node, ("ID", "RecipeID"))
        version = _direct_child_text(recipe_node, ("Version", "VersionID"))
        product = next(
            (
                (node.text or "").strip()
                for node in recipe_node.iter()
                if _local_name(node.tag) in {"ProductID", "ProductDefinitionID"}
                and (node.text or "").strip()
            ),
            "",
        )
        for key, value in (
            ("recipe_id", recipe_id),
            ("recipe_version", version),
            ("product_id", product),
        ):
            if value and value not in values[key]:
                values[key].append(value)
    for key in result:
        result[key] = ";".join(values[key])
    return result


def _direct_child_text(node: Any, names: tuple[str, ...]) -> str:
    for child in list(node):
        if _local_name(child.tag) in names and (child.text or "").strip():
            return (child.text or "").strip()
    return ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


__all__ = [
    "CacheEntry",
    "OpcUaRecordingManager",
    "ProcedureParameterRecord",
    "RecordingResult",
    "SignalDescriptor",
]
