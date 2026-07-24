import pytest

from src.backend import control
from src.backend import opcua_recording


def _install_execution(monkeypatch, events, *, main_error=None):
    procedure = object()
    mtps = object()
    monkeypatch.setattr(
        control,
        "build_execution_procedure",
        lambda recipe_files=None, mtp_files=None: (procedure, mtps),
    )

    def execute(received_procedure, received_mtps):
        assert received_procedure is procedure
        assert received_mtps is mtps
        events.append(("main",))
        if main_error is not None:
            raise main_error

    monkeypatch.setattr(control, "main", execute)
    return procedure


def test_recording_disabled_does_not_construct_or_run_recorder(monkeypatch):
    events = []
    _install_execution(monkeypatch, events)

    def unexpected_recorder(*args, **kwargs):
        pytest.fail("Recorder must not be constructed when recording is disabled")

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", unexpected_recorder)

    control.run_from_files(recording_enabled=False)

    assert events == [("main",)]


def test_recording_disabled_keeps_existing_history_file_unchanged(
    monkeypatch, tmp_path
):
    events = []
    _install_execution(monkeypatch, events)
    history_file = tmp_path / "lastRecord.csv"
    sentinel = b"existing-history-sentinel\r\n"
    history_file.write_bytes(sentinel)

    def unexpected_recorder(*args, **kwargs):
        pytest.fail("Recorder must not be constructed when recording is disabled")

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", unexpected_recorder)

    control.run_from_files(recording_enabled=False)

    assert events == [("main",)]
    assert history_file.read_bytes() == sentinel


def test_recorder_constructor_failure_logs_warning_and_main_continues(monkeypatch):
    events = []
    messages = []
    constructor_error = RuntimeError("recorder construction failed")
    _install_execution(monkeypatch, events)

    def failing_recorder(*args, **kwargs):
        events.append(("init",))
        raise constructor_error

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", failing_recorder)

    control.run_from_files(
        logger=messages.append,
        recording_enabled=True,
    )

    assert events == [("init",), ("main",)]
    assert any(
        message.startswith(
            "[HIST] Warning: RuntimeError: recorder construction failed"
        )
        and message.endswith("; recipe execution continues.")
        for message in messages
    )


def test_recording_starts_before_main_and_stops_completed(monkeypatch):
    events = []
    procedure = _install_execution(monkeypatch, events)

    class Recorder:
        def __init__(self, **kwargs):
            assert kwargs["procedure"] is procedure
            assert kwargs["recipe_files"] == ["recipe.xml"]
            assert kwargs["sampling_interval_s"] == 1.0
            assert callable(kwargs["logger"])
            events.append(("init",))

        def start(self):
            events.append(("start",))

        def stop(self, recipe_status, error=None):
            events.append(("stop", recipe_status, error))

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", Recorder)

    control.run_from_files(
        recipe_files=["recipe.xml"],
        recording_enabled=True,
    )

    assert events == [
        ("init",),
        ("start",),
        ("main",),
        ("stop", "completed", None),
    ]


def test_main_exception_stops_failed_and_preserves_original_exception(monkeypatch):
    events = []
    recipe_error = ValueError("recipe failed")
    _install_execution(monkeypatch, events, main_error=recipe_error)

    class Recorder:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            events.append(("start",))

        def stop(self, recipe_status, error=None):
            events.append(("stop", recipe_status, error))

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", Recorder)

    with pytest.raises(ValueError) as raised:
        control.run_from_files(recording_enabled=True)

    assert raised.value is recipe_error
    assert events == [
        ("start",),
        ("main",),
        ("stop", "failed", recipe_error),
    ]


def test_start_failure_logs_warning_and_recipe_execution_continues(monkeypatch):
    events = []
    messages = []
    start_error = RuntimeError("subscription setup failed")
    _install_execution(monkeypatch, events)

    class Recorder:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            events.append(("start",))
            raise start_error

        def stop(self, recipe_status, error=None):
            events.append(("stop", recipe_status, error))

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", Recorder)

    control.run_from_files(
        logger=messages.append,
        recording_enabled=True,
    )

    assert events == [
        ("start",),
        ("main",),
        ("stop", "completed", start_error),
    ]
    assert any(
        message.startswith("[HIST] Warning: RuntimeError: subscription setup failed")
        and message.endswith("; recipe execution continues.")
        for message in messages
    )


def test_stop_failure_logs_warning_without_failing_successful_recipe(monkeypatch):
    events = []
    messages = []
    _install_execution(monkeypatch, events)

    class Recorder:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            events.append(("start",))

        def stop(self, recipe_status, error=None):
            events.append(("stop", recipe_status, error))
            raise RuntimeError("CSV finalization failed")

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", Recorder)

    control.run_from_files(
        logger=messages.append,
        recording_enabled=True,
    )

    assert events == [
        ("start",),
        ("main",),
        ("stop", "completed", None),
    ]
    assert any(
        message.startswith("[HIST] Warning: RuntimeError: CSV finalization failed")
        and message.endswith("; recipe execution continues.")
        for message in messages
    )


def test_stop_failure_never_masks_original_recipe_exception(monkeypatch):
    events = []
    messages = []
    recipe_error = LookupError("original recipe error")
    _install_execution(monkeypatch, events, main_error=recipe_error)

    class Recorder:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            events.append(("start",))

        def stop(self, recipe_status, error=None):
            events.append(("stop", recipe_status, error))
            raise RuntimeError("secondary recorder error")

    monkeypatch.setattr(opcua_recording, "OpcUaRecordingManager", Recorder)

    with pytest.raises(LookupError) as raised:
        control.run_from_files(
            logger=messages.append,
            recording_enabled=True,
        )

    assert raised.value is recipe_error
    assert events == [
        ("start",),
        ("main",),
        ("stop", "failed", recipe_error),
    ]
    assert any(
        message.startswith("[HIST] Warning: RuntimeError: secondary recorder error")
        and message.endswith("; recipe execution continues.")
        for message in messages
    )
