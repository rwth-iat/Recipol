import asyncio
import csv
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.backend import opcua_recording as recording


def _parameter(
    name,
    parameter_type,
    channel,
    node_id,
    *,
    access="1",
    unit="",
):
    return SimpleNamespace(
        name=name,
        id=f"{name}-id",
        unit=unit,
        parameter_type=parameter_type,
        paramElem={
            channel: {
                "Type": "REAL",
                "ID": node_id,
                "Default": None,
                "Access": access,
            }
        },
    )


def _step(
    module,
    procedure_id,
    parameters,
    *,
    endpoint="opc.tcp://module:4840",
    namespace="urn:test:module",
):
    mtp = SimpleNamespace(
        name=module,
        url=endpoint,
        ns=namespace,
        source_file=f"{module}.aml",
    )
    inst = SimpleNamespace(
        name=f"Procedure {procedure_id}",
        id=f"instance-{procedure_id}",
        procId=procedure_id,
        serviceId=1,
        params=parameters,
    )
    return {"bml": object(), "mtp": mtp, "inst": inst, "params": []}


def test_catalog_selects_procedure_channels_deduplicates_and_filters_access(tmp_path):
    common = _parameter(
        "Temperature", "ProcessValueOut", "V", "Signals.Temp", unit="degC"
    )
    same_node = _parameter(
        "Temperature", "ProcessValueOut", "V", "Signals.Temp", unit="degC"
    )
    text_value = _parameter(
        "Batch name", "ProcessValueOut", "Text", "Signals.BatchName"
    )
    setpoint = _parameter(
        "Setpoint", "ProcedureParameter", "VOut", "Signals.Setpoint"
    )
    process_input = _parameter(
        "Target full", "ProcessValueIn", "V", "Signals.TargetFull", access="3"
    )
    write_only = _parameter(
        "Write only", "ProcessValueIn", "V", "Signals.WriteOnly", access="2"
    )
    unrelated = _parameter("Actor", "ActiveElement", "V", "Signals.Actor")

    manager = recording.OpcUaRecordingManager(
        [
            _step(
                "HC10",
                "10",
                [common, text_value, setpoint, process_input, write_only, unrelated],
            ),
            _step("HC10", "20", [same_node]),
            {"bml": object(), "mtp": None, "inst": None},
            ["parallel-step-is-not-top-level"],
        ],
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "record.csv",
    )

    signals, step_count = manager._build_signal_catalog()

    assert step_count == 2
    assert len(signals) == 4
    assert {(signal.signal_type, signal.channel) for signal in signals} == {
        ("ProcessValueOut", "V"),
        ("ProcessValueOut", "Text"),
        ("ProcedureParameter", "VOut"),
        ("ProcessValueIn", "V"),
    }
    temperature = next(signal for signal in signals if signal.node_address == "Signals.Temp")
    assert temperature.procedure_ids == {"10", "20"}
    assert all(signal.node_address != "Signals.WriteOnly" for signal in signals)


class _FakeStatus:
    def __init__(self, name="Good"):
        self.name = name

    def is_good(self):
        return self.name.startswith("Good")


class _FakeVariant:
    def __init__(self, value):
        self.Value = value


class _FakeDataValue:
    def __init__(self, value):
        self.Value = _FakeVariant(value)
        self.StatusCode = _FakeStatus()
        self.SourceTimestamp = datetime(2026, 7, 23, tzinfo=timezone.utc)
        self.ServerTimestamp = datetime(2026, 7, 23, tzinfo=timezone.utc)


class _FakeNodeId:
    def __init__(self, text):
        self.text = text

    def to_string(self):
        return self.text


class _FakeNode:
    def __init__(self, node_id):
        self.nodeid = _FakeNodeId(node_id)

    async def read_data_value(self):
        return _FakeDataValue(42.5)


class _FakeSubscription:
    def __init__(self, interval, handler):
        self.interval = interval
        self.handler = handler
        self.nodes = []
        self.sampling_interval = None
        self.deleted = False

    async def subscribe_data_change(self, nodes, sampling_interval=None):
        self.nodes = list(nodes)
        self.sampling_interval = sampling_interval
        return list(range(len(nodes)))

    async def delete(self):
        self.deleted = True


class _FakeClient:
    instances = []

    def __init__(self, url):
        self.url = url
        self.connected = False
        self.subscription = None
        self.__class__.instances.append(self)

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def get_namespace_index(self, uri):
        assert uri.startswith("urn:")
        return 4

    def get_node(self, node_id):
        return _FakeNode(node_id)

    async def create_subscription(self, interval, handler):
        self.subscription = _FakeSubscription(interval, handler)
        return self.subscription

    async def check_connection(self):
        if not self.connected:
            raise ConnectionError("disconnected")


def test_start_uses_one_client_and_subscription_per_module(monkeypatch, tmp_path):
    _FakeClient.instances.clear()
    monkeypatch.setattr(recording, "Client", _FakeClient)
    procedure = [
        _step(
            "HC10",
            "10",
            [_parameter("Temperature", "ProcessValueOut", "V", "Temp")],
            endpoint="opc.tcp://hc10",
            namespace="urn:hc10",
        ),
        _step(
            "HC10",
            "20",
            [_parameter("Level", "ProcessValueOut", "V", "Level")],
            endpoint="opc.tcp://hc10",
            namespace="urn:hc10",
        ),
        _step(
            "HC20",
            "30",
            [_parameter("Flow", "ProcessValueOut", "V", "Flow")],
            endpoint="opc.tcp://hc20",
            namespace="urn:hc20",
        ),
    ]
    manager = recording.OpcUaRecordingManager(
        procedure,
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )
    ready_states = []
    original_record_snapshot = manager._record_snapshot

    def record_snapshot(*args, **kwargs):
        ready_states.append(manager._ready.is_set())
        return original_record_snapshot(*args, **kwargs)

    monkeypatch.setattr(manager, "_record_snapshot", record_snapshot)

    manager.start()
    result = manager.stop("completed")

    assert len(_FakeClient.instances) == 2
    assert all(client.subscription.interval == 1000 for client in _FakeClient.instances)
    assert all(
        client.subscription.sampling_interval == 1000
        for client in _FakeClient.instances
    )
    assert all(not client.connected for client in _FakeClient.instances)
    assert result.status == "completed"
    assert result.snapshot_count >= 1
    assert ready_states[0] is False


def test_csv_contains_metadata_wide_values_quality_and_replaces_existing(
    monkeypatch, tmp_path
):
    _FakeClient.instances.clear()
    monkeypatch.setattr(recording, "Client", _FakeClient)
    recipe = tmp_path / "recipe.xml"
    recipe.write_text(
        """<?xml version="1.0"?>
        <BatchInformation xmlns="http://www.mesa.org/xml/B2MML">
          <MasterRecipe>
            <ID>Recipe-42</ID><Version>3</Version>
            <Header><ProductID>Product-A</ProductID></Header>
          </MasterRecipe>
        </BatchInformation>""",
        encoding="utf-8",
    )
    output = tmp_path / "lastRecord.csv"
    output.write_text("old data", encoding="utf-8")
    messages = []
    manager = recording.OpcUaRecordingManager(
        [
            _step(
                "HC10",
                "10",
                [_parameter("Temperature", "ProcessValueOut", "V", "Temp")],
                endpoint="opc.tcp://hc10",
                namespace="urn:hc10",
            )
        ],
        [recipe],
        logger=messages.append,
        output_path=output,
    )

    manager.start()
    result = manager.stop("failed", RuntimeError("service failure"))

    rows = list(csv.reader(output.open(encoding="utf-8", newline="")))
    blank_index = rows.index([])
    metadata = dict(row for row in rows[:blank_index])
    header = rows[blank_index + 1]
    data = rows[blank_index + 2 :]

    assert metadata["recipe_id"] == "Recipe-42"
    assert metadata["recipe_version"] == "3"
    assert metadata["product_id"] == "Product-A"
    assert metadata["recipe_files"] == "recipe.xml"
    assert metadata["recipe_status"] == "failed"
    assert metadata["recording_status"] == "partial"
    assert metadata["sampling_interval_s"] == "1"
    assert metadata["modules"] == "HC10"
    assert metadata["error"] == "RuntimeError: service failure"
    assert header[0] == "timestamp_utc"
    assert header[1].endswith(".value")
    assert header[2].endswith(".quality")
    assert data
    assert data[0][1:] == ["42.5", "Good"]
    assert result.status == "partial"
    assert any(message.startswith("[HIST] Recording started:") for message in messages)
    assert any(message.startswith("[HIST] Recording stopped:") for message in messages)
    assert not list(tmp_path.glob(".lastRecord.*.tmp"))


def test_boolean_csv_value_and_missing_quality(tmp_path):
    signal = recording.SignalDescriptor(
        endpoint="opc.tcp://hc10",
        namespace="urn:hc10",
        node_address="Full",
        module_name="HC10",
        signal_type="ProcessValueIn",
        signal_name="Target full",
        channel="V",
        procedure_ids={"10"},
    )
    text_signal = recording.SignalDescriptor(
        endpoint="opc.tcp://hc10",
        namespace="urn:hc10",
        node_address="BatchName",
        module_name="HC10",
        signal_type="ProcessValueOut",
        signal_name="Chargenname, äußere Linie",
        channel="Text",
        procedure_ids={"10"},
    )

    manager = recording.OpcUaRecordingManager(
        [],
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )
    manager.signals = [signal, text_signal]
    manager.started_at = datetime.now(timezone.utc)
    manager._open_spool()
    manager._update_cache(signal.key, recording.CacheEntry(True, "Good"))
    text_value = 'Los 7, "überfüllt"'
    manager._update_cache(text_signal.key, recording.CacheEntry(text_value, "Good"))
    manager._record_snapshot(datetime(2026, 7, 23, tzinfo=timezone.utc))
    manager._update_cache(signal.key, recording.CacheEntry(None, "Missing"))
    manager._record_snapshot(datetime(2026, 7, 23, 0, 0, 1, tzinfo=timezone.utc))
    manager._started = True

    manager.stop("completed")

    rows = list(csv.reader((tmp_path / "lastRecord.csv").open(encoding="utf-8")))
    blank_index = rows.index([])
    header = rows[blank_index + 1]
    data = rows[blank_index + 2 :]
    assert data[0][0] == "2026-07-23T00:00:00Z"
    assert data[1][0] == "2026-07-23T00:00:01Z"
    assert f"{text_signal.column_name}.value" in header
    assert data[0][1:] == ["true", "Good", text_value, "Good"]


@pytest.mark.parametrize(
    ("status", "error", "expected"),
    [
        ("completed", None, "completed"),
        ("failed", RuntimeError("boom"), "partial"),
    ],
)
def test_recording_status_tracks_recipe_outcome(status, error, expected, tmp_path):
    manager = recording.OpcUaRecordingManager(
        [],
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )
    manager.signals = [
        recording.SignalDescriptor(
            "url", "ns", "node", "module", "ProcessValueOut", "value", "V"
        )
    ]
    manager._active_group_count = 1
    assert manager._recording_status(status, error) == expected

class _MixedSubscription(_FakeSubscription):
    async def subscribe_data_change(self, nodes, sampling_interval=None):
        self.nodes = list(nodes)
        self.sampling_interval = sampling_interval
        return [0, _FakeStatus("BadMonitoredItemIdInvalid")]


class _MixedClient(_FakeClient):
    async def create_subscription(self, interval, handler):
        self.subscription = _MixedSubscription(interval, handler)
        return self.subscription


def test_mixed_subscription_results_keep_only_successful_nodes(monkeypatch, tmp_path):
    _MixedClient.instances.clear()
    monkeypatch.setattr(recording, "Client", _MixedClient)
    messages = []
    procedure = [
        _step(
            "HC10",
            "10",
            [
                _parameter("Accepted", "ProcessValueOut", "V", "A.Good"),
                _parameter("Rejected", "ProcessValueOut", "V", "B.Rejected"),
            ],
            endpoint="opc.tcp://hc10",
            namespace="urn:hc10",
        )
    ]
    manager = recording.OpcUaRecordingManager(
        procedure,
        [],
        logger=messages.append,
        output_path=tmp_path / "lastRecord.csv",
    )

    manager.start()
    connection = next(iter(manager._connections.values()))
    rejected = next(signal for signal in manager.signals if signal.node_address == "B.Rejected")

    assert [signal.node_address for signal in connection.signals] == ["A.Good"]
    assert len(connection.nodes) == 1
    assert manager._cache[rejected.key].quality == "Missing"
    assert any("subscribed 1 signal(s)" in message for message in messages)
    assert any("BadMonitoredItemIdInvalid" in message for message in messages)

    result = manager.stop("completed")
    assert result.status == "partial"


def test_bad_wrapped_status_marks_group_unavailable_and_forces_reconnect(
    monkeypatch, tmp_path
):
    signal = recording.SignalDescriptor(
        "opc.tcp://hc10",
        "urn:hc10",
        "Temperature",
        "HC10",
        "ProcessValueOut",
        "Temperature",
        "V",
    )
    manager = recording.OpcUaRecordingManager(
        [],
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )
    manager.signals = [signal]
    manager._update_cache(signal.key, recording.CacheEntry(21.5, "Good"))
    group_key = signal.group_key
    handler = recording._SubscriptionHandler(manager, group_key)

    handler.status_change_notification(
        SimpleNamespace(Status=_FakeStatus("BadTimeout"))
    )

    assert group_key in manager._unavailable_groups
    assert manager._cache[signal.key].quality == "BadNoCommunication"

    warning_count = len(manager._warnings)
    manager._stopped = True
    handler.status_change_notification(
        SimpleNamespace(Status=_FakeStatus("BadSessionClosed"))
    )
    assert len(manager._warnings) == warning_count
    manager._stopped = False

    events = []
    manager._connections[group_key] = recording._Connection(
        client=object(), subscription=None, nodes=[], signals=[signal]
    )
    manager._reconnect_interval_s = 0.001

    async def disconnect(key):
        events.append(("disconnect", key))
        manager._connections.pop(key, None)

    async def connect(key, signals):
        events.append(("connect", key, list(signals)))
        manager._unavailable_groups.discard(key)
        manager._async_stop.set()
        return True

    monkeypatch.setattr(manager, "_disconnect_group", disconnect)
    monkeypatch.setattr(manager, "_connect_group", connect)

    async def exercise_reconnect():
        manager._async_stop = asyncio.Event()
        await asyncio.wait_for(
            manager._reconnect_loop({group_key: [signal]}), timeout=0.2
        )

    asyncio.run(exercise_reconnect())

    assert [event[0] for event in events] == ["disconnect", "connect"]
    assert events[1][2] == [signal]


def test_run_propagates_sampler_failure_even_when_stop_completes_and_cleans_up(
    monkeypatch, tmp_path
):
    manager = recording.OpcUaRecordingManager(
        [],
        [],
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )
    group_key = ("opc.tcp://hc10", "urn:hc10", "HC10")
    manager._connections[group_key] = recording._Connection(
        client=object(), subscription=None, nodes=[], signals=[]
    )
    disconnected = []

    async def broken_sampler():
        manager._async_stop.set()
        raise RuntimeError("sampler exploded")

    async def pending_reconnector(_groups):
        await asyncio.Future()

    async def disconnect(key):
        disconnected.append(key)
        manager._connections.pop(key, None)

    monkeypatch.setattr(manager, "_sample_loop", broken_sampler)
    monkeypatch.setattr(manager, "_reconnect_loop", pending_reconnector)
    monkeypatch.setattr(manager, "_disconnect_group", disconnect)

    with pytest.raises(RuntimeError, match="sampler exploded"):
        asyncio.run(manager._run())

    assert disconnected == [group_key]
    assert manager._connections == {}
    assert manager._run_task is None
    assert manager._ready.is_set()

def test_data_value_quality_comes_from_opcua_status_code():
    data_value = SimpleNamespace(
        Value=_FakeVariant(19.75),
        StatusCode=_FakeStatus("BadSensorFailure"),
        SourceTimestamp=datetime(2026, 7, 23, tzinfo=timezone.utc),
        ServerTimestamp=datetime(2026, 7, 23, 0, 0, 1, tzinfo=timezone.utc),
    )

    value, quality, source_ts, server_ts = recording._parse_data_value(data_value)

    assert value == 19.75
    assert quality == "BadSensorFailure"
    assert source_ts == datetime(2026, 7, 23, tzinfo=timezone.utc)
    assert server_ts == datetime(2026, 7, 23, 0, 0, 1, tzinfo=timezone.utc)


def test_missing_asyncua_client_finalizes_failed_recording(monkeypatch, tmp_path):
    monkeypatch.setattr(recording, "Client", None)
    messages = []
    manager = recording.OpcUaRecordingManager(
        [
            _step(
                "HC10",
                "10",
                [_parameter("Temperature", "ProcessValueOut", "V", "Temp")],
                endpoint="opc.tcp://hc10",
                namespace="urn:hc10",
            )
        ],
        [],
        logger=messages.append,
        output_path=tmp_path / "lastRecord.csv",
    )

    manager.start()
    result = manager.stop("completed")

    rows = list(
        csv.reader((tmp_path / "lastRecord.csv").open(encoding="utf-8"))
    )
    metadata = dict(row for row in rows[: rows.index([])])

    assert result.status == "failed"
    assert result.snapshot_count == 0
    assert metadata["recording_status"] == "failed"
    assert any(
        "asyncua is not installed" in message for message in messages
    )
    assert sum(
        message.startswith("[HIST] Recording started:")
        for message in messages
    ) == 1
    assert any(message.startswith("[HIST] Recording stopped:") for message in messages)

