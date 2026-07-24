import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QWidget


class _SwitchButton(QCheckBox):
    def setOnText(self, text):
        self._on_text = text

    def setOffText(self, text):
        self._off_text = text

    def getOnText(self):
        return self._on_text

    def getOffText(self):
        return self._off_text


fluent_widgets = ModuleType("qfluentwidgets")
fluent_widgets.CardWidget = QWidget
fluent_widgets.ComboBox = QComboBox
fluent_widgets.FluentIcon = SimpleNamespace(DOCUMENT=object())
fluent_widgets.InfoBar = SimpleNamespace(error=lambda **kwargs: None)
fluent_widgets.InfoBarPosition = SimpleNamespace(TOP_RIGHT=object())
fluent_widgets.PrimaryPushButton = QPushButton
fluent_widgets.SubtitleLabel = QLabel
fluent_widgets.SwitchButton = _SwitchButton
fluent_widgets.TitleLabel = QLabel
_missing_module = object()
_previous_fluent_widgets = sys.modules.get("qfluentwidgets", _missing_module)
sys.modules["qfluentwidgets"] = fluent_widgets

_MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "frontend" / "SFCMonitor.py"
_SPEC = importlib.util.spec_from_file_location("sfc_monitor_under_test", _MODULE_PATH)
_SFC_MONITOR = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _SFC_MONITOR
try:
    _SPEC.loader.exec_module(_SFC_MONITOR)
finally:
    if _previous_fluent_widgets is _missing_module:
        sys.modules.pop("qfluentwidgets", None)
    else:
        sys.modules["qfluentwidgets"] = _previous_fluent_widgets

ControlRunner = _SFC_MONITOR.ControlRunner
SFCMonitor = _SFC_MONITOR.SFCMonitor


def _application():
    return QApplication.instance() or QApplication([])


class _WindowWithHome(QWidget):
    def __init__(self):
        super().__init__()
        self.home_page = SimpleNamespace(
            last_run_has_aml=True,
            last_mtp_files=["module.aml"],
            last_recipe_files=["recipe.xml"],
        )


def test_recording_switch_is_right_of_execute_button_and_defaults_off():
    app = _application()
    monitor = SFCMonitor()

    execute_index = monitor.selection_layout.indexOf(monitor.execute_button)
    recording_index = monitor.selection_layout.indexOf(monitor.recording_switch)

    assert recording_index == execute_index + 1
    assert monitor.recording_switch.isChecked() is False
    assert monitor.recording_switch.getOnText() == "Start Recording"
    assert monitor.recording_switch.getOffText() == "Start Recording"

    monitor.deleteLater()
    app.processEvents()


def test_execute_snapshots_recording_state_and_disables_controls(monkeypatch):
    app = _application()
    window = _WindowWithHome()
    monitor = SFCMonitor(parent=window)
    monitor.recording_switch.setChecked(True)
    monkeypatch.setattr(QThread, "start", lambda self: None)

    monitor._on_execute_recipe()

    assert monitor._control_runner._recording_enabled is True
    assert monitor.execute_button.isEnabled() is False
    assert monitor.recording_switch.isEnabled() is False

    monitor._restore_execution_controls()

    assert monitor.execute_button.isEnabled() is True
    assert monitor.recording_switch.isEnabled() is True
    assert monitor.recording_switch.isChecked() is True

    monitor._control_thread.quit()
    monitor.deleteLater()
    window.deleteLater()
    app.processEvents()


def test_sync_execute_button_stays_disabled_during_active_run():
    app = _application()
    window = _WindowWithHome()
    monitor = SFCMonitor(parent=window)
    monitor._control_thread = SimpleNamespace(isRunning=lambda: True)
    monitor.execute_button.setEnabled(True)

    monitor.update_data([])

    assert monitor.execute_button.isEnabled() is False

    monitor._control_thread = None
    monitor.deleteLater()
    window.deleteLater()
    app.processEvents()


def test_control_runner_forwards_recording_and_logs_success(monkeypatch):
    calls = []
    backend_package = ModuleType("backend")
    backend_control = ModuleType("backend.control")

    def run_from_files(**kwargs):
        calls.append(kwargs)

    backend_control.run_from_files = run_from_files
    backend_package.control = backend_control
    monkeypatch.setitem(sys.modules, "backend", backend_package)
    monkeypatch.setitem(sys.modules, "backend.control", backend_control)

    runner = ControlRunner(
        mtp_files=["module.aml"],
        recipe_files=["recipe.xml"],
        recording_enabled=True,
    )
    logs = []
    errors = []
    runner.log_signal.connect(logs.append)
    runner.error.connect(errors.append)

    runner.run()

    assert len(calls) == 1
    assert calls[0]["mtp_files"] == ["module.aml"]
    assert calls[0]["recipe_files"] == ["recipe.xml"]
    assert calls[0]["recording_enabled"] is True
    assert calls[0]["logger"] == runner._handle_log
    assert logs == ["[EXEC] Recipe execution completed successfully."]
    assert errors == []


def test_control_runner_logs_failure_without_hiding_traceback(monkeypatch):
    backend_package = ModuleType("backend")
    backend_control = ModuleType("backend.control")

    def run_from_files(**kwargs):
        raise RuntimeError("OPC UA unavailable")

    backend_control.run_from_files = run_from_files
    backend_package.control = backend_control
    monkeypatch.setitem(sys.modules, "backend", backend_package)
    monkeypatch.setitem(sys.modules, "backend.control", backend_control)

    runner = ControlRunner(recording_enabled=False)
    logs = []
    errors = []
    runner.log_signal.connect(logs.append)
    runner.error.connect(errors.append)

    runner.run()

    assert logs == ["[EXEC] Recipe execution failed: RuntimeError: OPC UA unavailable."]
    assert len(errors) == 1
    assert "RuntimeError: OPC UA unavailable" in errors[0]
