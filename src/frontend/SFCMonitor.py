# src/frontend/SFCMonitor.py
# -*- coding: utf-8 -*-

import math
import re

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, QObject, QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF, QTextOption
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import CardWidget, ComboBox, FluentIcon, SubtitleLabel, TitleLabel, PrimaryPushButton, InfoBar, InfoBarPosition

class ControlRunner(QObject):
    input_requested = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    exec_signal = pyqtSignal(str, str)

    def __init__(self, mtp_files=None, recipe_files=None):
        super().__init__()
        self._mutex = QMutex()
        self._wait = QWaitCondition()
        self._input_response = ""
        self._mtp_files = mtp_files or []
        self._recipe_files = recipe_files or []

    def run(self):
        import builtins
        import traceback
        # import Code.Recipol.control as control
        from backend import control

        original_input = builtins.input

        def _input(prompt: str = "") -> str:
            self._mutex.lock()
            try:
                self._input_response = ""
                self.input_requested.emit(str(prompt))
                self._wait.wait(self._mutex)
                return self._input_response
            finally:
                self._mutex.unlock()

        builtins.input = _input
        try:
            control.run_from_files(mtp_files=self._mtp_files, recipe_files=self._recipe_files, logger=self._handle_log)
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            builtins.input = original_input
            self.finished.emit()

    def _handle_log(self, msg: str):
        msg = str(msg)
        self.log_signal.emit(msg)
        if msg.startswith("[EXEC] Running step '"):
            tail = msg[len("[EXEC] Running step '"):]
            step_name = tail.split("'", 1)[0]
            if step_name:
                self.exec_signal.emit("step", step_name)
            return
        if msg.startswith("[EXEC] Transition " ):
            cond = msg[len("[EXEC] Transition " ):].strip()
            if cond:
                self.exec_signal.emit("transition", cond)
            return

    def provide_input(self, text: str):
        self._mutex.lock()
        try:
            self._input_response = text
            self._wait.wakeAll()
        finally:
            self._mutex.unlock()



class SFCGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(1.12, 1.12)
        else:
            self.scale(1 / 1.12, 1 / 1.12)
        event.accept()


class DraggableNodeItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self._edges = []

    def add_edge(self, edge):
        self._edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self._edges:
                edge.update()
        return super().itemChange(change, value)


class SFCEdge:
    def __init__(self, start_node: DraggableNodeItem, end_node: DraggableNodeItem, scene: QGraphicsScene, pen: QPen):
        self.start_node = start_node
        self.end_node = end_node
        self.scene = scene
        self.pen = pen
        self.segments = []
        self.arrow_item = self.scene.addPolygon(QPolygonF(), self.pen, QBrush(self.pen.color()))

    def _set_segment_count(self, count: int):
        while len(self.segments) < count:
            self.segments.append(self.scene.addLine(0, 0, 0, 0, self.pen))
        while len(self.segments) > count:
            item = self.segments.pop()
            self.scene.removeItem(item)

    def update(self):
        start_rect = self.start_node.sceneBoundingRect()
        end_rect = self.end_node.sceneBoundingRect()
        start = QPointF(start_rect.center().x(), start_rect.bottom())
        end = QPointF(end_rect.center().x(), end_rect.top())

        clear = 18.0
        if end.y() >= start.y():
            mid_y = start.y() + clear
            points = [
                start,
                QPointF(start.x(), mid_y),
                QPointF(end.x(), mid_y),
                end,
            ]
        else:
            side_x = (start_rect.center().x() + end_rect.center().x()) / 2.0
            y1 = start.y() + clear
            y2 = end.y() - clear
            points = [
                start,
                QPointF(start.x(), y1),
                QPointF(side_x, y1),
                QPointF(side_x, y2),
                QPointF(end.x(), y2),
                end,
            ]

        self._set_segment_count(max(0, len(points) - 1))
        for i, (p1, p2) in enumerate(zip(points, points[1:])):
            self.segments[i].setLine(p1.x(), p1.y(), p2.x(), p2.y())

        p_last = points[-2]
        p_end = points[-1]
        dx = p_end.x() - p_last.x()
        dy = p_end.y() - p_last.y()
        length = math.hypot(dx, dy)
        if length < 1e-6:
            self.arrow_item.setPolygon(QPolygonF())
            return

        ux, uy = dx / length, dy / length
        head_len = 10.0
        head_w = 6.0
        tip = p_end
        base = QPointF(p_end.x() - ux * head_len, p_end.y() - uy * head_len)
        left = QPointF(base.x() - uy * head_w, base.y() + ux * head_w)
        right = QPointF(base.x() + uy * head_w, base.y() - ux * head_w)
        self.arrow_item.setPolygon(QPolygonF([tip, left, right]))


class SFCMonitor(QWidget):
    def __init__(self, log_callback=None, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("RecipeMonitor")
        self.sfc_rows = []
        self.recipe_groups = []
        self._start_step_seq = None
        self._end_step_seq = None

        self._control_thread = None
        self._control_runner = None
        self.log_callback = log_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        self.title = TitleLabel("Recipe Monitor", self)
        self.subtitle = SubtitleLabel("Sequential Function Chart", self)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)

        self.selection_card = CardWidget(self)
        self.selection_layout = QHBoxLayout(self.selection_card)
        self.recipe_combo = ComboBox(self)
        self.recipe_combo.setPlaceholderText("Select a recipe to view")
        self.recipe_combo.setMinimumWidth(320)
        self.recipe_combo.currentIndexChanged.connect(self._on_recipe_changed)
        self.selection_layout.addWidget(self.recipe_combo)
        self.execute_button = PrimaryPushButton("Execute Recipe", self)
        self.execute_button.setEnabled(False)
        self.execute_button.clicked.connect(self._on_execute_recipe)
        self.selection_layout.addWidget(self.execute_button)
        self.selection_layout.addStretch(1)
        layout.addWidget(self.selection_card)

        self.scene = QGraphicsScene(self)
        self.view = SFCGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.view.setStyleSheet("QGraphicsView { border: 1px solid #303030; background: #151515; }")
        layout.addWidget(self.view, 1)
        self._build_zoom_controls()

        self._pen_line = QPen(QColor("#c7c7c7"), 1.5)
        self._pen_step = QPen(QColor("#71b7ff"), 2)
        self._pen_trans = QPen(QColor("#f6c05a"), 2)
        self._brush_step = QBrush(QColor("#1f3f63"))
        self._brush_trans = QBrush(QColor("#4f3a16"))
        self._font_main = QFont("Segoe UI", 9)
        self._font_sub = QFont("Segoe UI", 8)
        # Step font increased by ~30%.
        self._font_step = QFont("Segoe UI", 16)
        self._pen_active = QPen(QColor("#6dff7a"), 3)
        self._brush_active = QBrush(QColor("#39ff14"))
        self._step_nodes = {}
        self._transition_nodes = {}
        self._step_nodes_all = []
        self._transition_nodes_all = []
        self._init_nodes = []
        self._end_nodes = []
        self._last_highlight_kind = None
        self._highlight_token = 0
        self._pending_transition_nodes = []

    def update_data(self, sfc_rows: list):
        self._sync_execute_button()
        self.sfc_rows = sorted((sfc_rows or []), key=lambda x: x.get("seq", 0))
        self.recipe_groups = []

        self.recipe_combo.blockSignals(True)
        self.recipe_combo.clear()

        if not self.sfc_rows:
            self.recipe_combo.setPlaceholderText("No SFC data to display")
            self.recipe_combo.blockSignals(False)
            self._render_rows([])
            return

        self.recipe_combo.setPlaceholderText("Select a recipe to view")
        grouped: dict[str, list[dict]] = {}
        for row in self.sfc_rows:
            recipe_name = str(row.get("recipe", "Unknown Recipe"))
            grouped.setdefault(recipe_name, []).append(row)

        self.recipe_groups = list(grouped.items())
        for recipe_name, _ in self.recipe_groups:
            self.recipe_combo.addItem(recipe_name, icon=FluentIcon.DOCUMENT)

        self.recipe_combo.blockSignals(False)

        if self.recipe_combo.count() > 0:
            self.recipe_combo.setCurrentIndex(0)
            self._on_recipe_changed(0)
        else:
            self._render_rows([])


    def _on_recipe_changed(self, index: int):
        if index < 0 or index >= len(self.recipe_groups):
            self._render_rows([])
            return
        _, rows = self.recipe_groups[index]
        self._render_rows(rows)

    def _render_rows(self, rows: list[dict]):
        self.scene.clear()
        self._start_step_seq = None
        self._end_step_seq = None
        self._step_nodes = {}
        self._transition_nodes = {}
        self._step_nodes_all = []
        self._transition_nodes_all = []
        self._init_nodes = []
        self._end_nodes = []
        self._last_highlight_kind = None
        self._highlight_token = 0
        self._pending_transition_nodes = []

        if not rows:
            txt = self.scene.addText("No SFC data to display", self._font_main)
            txt.setDefaultTextColor(QColor("#ffffff"))
            txt.setPos(24, 20)
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-30, -20, 120, 40))
            return

        step_seqs = [row.get("seq") for row in rows if str(row.get("kind", "")).lower() == "step"]
        if step_seqs:
            self._start_step_seq = step_seqs[0]
            self._end_step_seq = step_seqs[-1]

        levels = self._build_levels(rows)
        self._draw_levels(levels)
        # Make initial view identical to pressing Reset once after render.
        QTimer.singleShot(0, self._fit_to_width_80)
        QTimer.singleShot(80, self._fit_to_width_80)

    def _build_levels(self, rows: list) -> list[list[dict]]:
        levels = []
        i = 0
        while i < len(rows):
            row = rows[i]
            if row.get("parallel"):
                group = [row]
                i += 1
                while i < len(rows) and rows[i].get("parallel"):
                    group.append(rows[i])
                    i += 1
                levels.append(group)
            else:
                levels.append([row])
                i += 1
        return levels

    def _draw_levels(self, levels: list[list[dict]]):
        top_y = 30.0
        y = top_y
        col_idx = 0
        col_step = 620.0
        # Roughly 3 Steps + 3 Transitions per column.
        max_col_height = 760.0
        x_gap = 60.0
        y_gap = 80.0
        prev_anchors = []

        for level in levels:
            center_x = 380.0 + col_idx * col_step
            size_list = [self._node_size(r) for r in level]
            total_w = sum(w for w, _ in size_list) + x_gap * (len(level) - 1)
            x = center_x - total_w / 2

            level_anchors = []
            max_h = 0.0
            for row, (w, h) in zip(level, size_list):
                rect = QRectF(x, y, w, h)
                node_item = self._draw_node(row, rect)
                node_rect = node_item.sceneBoundingRect()
                top = QPointF(node_rect.center().x(), node_rect.top())
                bottom = QPointF(node_rect.center().x(), node_rect.bottom())
                level_anchors.append({"top": top, "bottom": bottom, "node": node_item})
                max_h = max(max_h, h)
                x += w + x_gap

            if prev_anchors:
                for prev in prev_anchors:
                    for curr in level_anchors:
                        self._draw_arrow_orthogonal(
                            prev["node"],
                            curr["node"],
                        )

            prev_anchors = level_anchors
            y += max_h + y_gap
            if y + max_h > max_col_height:
                # Start a new column and continue the flow with connecting arrows.
                y = top_y
                col_idx += 1

        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-30, -20, 120, 40))

    def _on_execute_recipe(self):
        if self._control_thread and self._control_thread.isRunning():
            QMessageBox.information(self, "Execute Recipe", "Recipe execution is already running.")
            return

        self.execute_button.setEnabled(False)
        self._control_thread = QThread(self)
        mtp_files, recipe_files = self._get_selected_files()
        if mtp_files is None and recipe_files is None:
            QMessageBox.information(self, "Execute Recipe", "No selected files found from Home page. Please select files and run Inspect first.")
            self.execute_button.setEnabled(True)
            return

        self._control_runner = ControlRunner(mtp_files=mtp_files or [], recipe_files=recipe_files or [])
        self._control_runner.moveToThread(self._control_thread)
        self._control_runner.log_signal.connect(self._append_log)
        self._control_runner.exec_signal.connect(self._on_exec_event)

        self._control_thread.started.connect(self._control_runner.run)
        self._control_runner.input_requested.connect(self._prompt_for_input)
        self._control_runner.error.connect(self._handle_control_error)
        self._control_runner.finished.connect(self._on_exec_finished)
        self._control_runner.finished.connect(self._control_thread.quit)
        self._control_runner.finished.connect(self._control_runner.deleteLater)
        self._control_thread.finished.connect(self._control_thread.deleteLater)
        self._control_thread.finished.connect(self._clear_control_runner)
        self._control_thread.finished.connect(lambda: self.execute_button.setEnabled(True))

        self._highlight_init()
        self._control_thread.start()

    def _sync_execute_button(self):
        self.execute_button.setEnabled(self._home_has_aml())

    def _home_has_aml(self) -> bool:
        main_win = self.window()
        if not main_win or not hasattr(main_win, "home_page"):
            return False
        home = main_win.home_page
        if getattr(home, "last_run_has_aml", False):
            return True
        mtp_files = getattr(home, "last_mtp_files", None)
        return bool(mtp_files)


    def _clear_control_runner(self):
        self._control_thread = None
        self._control_runner = None

    def _append_log(self, msg: str):
        if self.log_callback:
            self.log_callback(msg)

    def _get_selected_files(self):
        main_win = self.window()
        if not main_win or not hasattr(main_win, "home_page"):
            return None, None
        home = main_win.home_page
        mtp_files = getattr(home, "last_mtp_files", None)
        recipe_files = getattr(home, "last_recipe_files", None)
        if mtp_files is None and recipe_files is None:
            return None, None
        return mtp_files or [], recipe_files or []

    def _prompt_for_input(self, prompt: str):
        text, ok = QInputDialog.getText(self, "Execute Recipe", prompt)
        if not ok:
            text = ""
        if self._control_runner:
            self._control_runner.provide_input(text)

    def _handle_control_error(self, traceback_text: str):
        if "OPC UA Connection Failed" in traceback_text or "TimeoutError" in traceback_text or "connect_socket" in traceback_text:
            InfoBar.error(
                title="OPC UA Connection Failed",
                content="",
                duration=5000,
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )

        dialog = QDialog(self)
        dialog.setWindowTitle("Execute Recipe")
        dialog.setMinimumWidth(640)

        layout = QVBoxLayout(dialog)
        box = QTextEdit(dialog)
        box.setReadOnly(True)
        box.setPlainText(traceback_text)
        box.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        layout.addWidget(box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()

    def _build_zoom_controls(self):
        self.zoom_container = QWidget(self.view.viewport())
        self.zoom_container.setStyleSheet(
            "QWidget { background: rgba(22, 22, 22, 200); border: 1px solid #404040; border-radius: 10px; }"
        )
        row = QHBoxLayout(self.zoom_container)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(6)

        self.btn_zoom_out = QPushButton("-", self.zoom_container)
        self.btn_zoom_in = QPushButton("+", self.zoom_container)
        self.btn_zoom_reset = QPushButton("Reset", self.zoom_container)
        for btn in (self.btn_zoom_out, self.btn_zoom_in, self.btn_zoom_reset):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { color: white; background: #2a2a2a; border: 1px solid #4a4a4a; border-radius: 6px; padding: 4px 8px; }"
                "QPushButton:hover { background: #3a3a3a; }"
                "QPushButton:pressed { background: #202020; }"
            )
        self.btn_zoom_out.setFixedWidth(28)
        self.btn_zoom_in.setFixedWidth(28)

        self.btn_zoom_out.clicked.connect(lambda: self.view.scale(1 / 1.15, 1 / 1.15))
        self.btn_zoom_in.clicked.connect(lambda: self.view.scale(1.15, 1.15))
        self.btn_zoom_reset.clicked.connect(self._fit_to_width_80)

        row.addWidget(self.btn_zoom_out)
        row.addWidget(self.btn_zoom_in)
        row.addWidget(self.btn_zoom_reset)
        self.zoom_container.adjustSize()
        QTimer.singleShot(0, self._position_zoom_controls)

    def _position_zoom_controls(self):
        if not hasattr(self, "zoom_container"):
            return
        pad = 14
        size = self.zoom_container.sizeHint()
        self.zoom_container.move(
            self.view.viewport().width() - size.width() - pad,
            pad,
        )
        self.zoom_container.raise_()

    def _fit_to_width_80(self):
        rect = self.scene.sceneRect()
        if rect.isEmpty():
            return
        self.view.resetTransform()
        viewport_w = max(1, self.view.viewport().width())
        viewport_h = max(1, self.view.viewport().height())
        scale_x = (viewport_w * 0.90) / max(1.0, rect.width())
        scale_y = (viewport_h * 0.90) / max(1.0, rect.height())
        scale = min(scale_x, scale_y)
        self.view.scale(scale, scale)
        self.view.centerOn(rect.center())
        self._position_zoom_controls()

    def _node_size(self, row: dict) -> tuple[float, float]:
        if str(row.get("kind", "")).lower() == "transition":
            return 180.0, 28.0
        # Step box enlarged to ~1.3x.
        return 312.0, 112.0

    def _normalize_key(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip()

    def _register_node(self, row: dict, node_item: DraggableNodeItem):
        kind = str(row.get("kind", "")).lower()
        if kind == "transition":
            key = self._normalize_key(str(row.get("condition", "")))
            self._transition_nodes_all.append(node_item)
            if key:
                self._transition_nodes.setdefault(key, []).append(node_item)
        else:
            key = self._normalize_key(str(row.get("name", "")))
            self._step_nodes_all.append(node_item)
            if key:
                self._step_nodes.setdefault(key, []).append(node_item)

    def _reset_node_styles(self):
        for node in self._step_nodes_all:
            node.setPen(self._pen_step)
            node.setBrush(self._brush_step)
        for node in self._transition_nodes_all:
            node.setPen(self._pen_trans)
            node.setBrush(self._brush_trans)

    def _highlight_nodes(self, nodes: list[DraggableNodeItem]):
        for node in nodes:
            node.setPen(self._pen_active)
            node.setBrush(self._brush_active)

    def _flash_transition_then_step(self, token: int, step_nodes: list[DraggableNodeItem]):
        if token != self._highlight_token:
            return
        # After the brief transition flash, highlight the next step.
        self._reset_node_styles()
        self._highlight_nodes(step_nodes)
        self._last_highlight_kind = "step"

    def _on_exec_event(self, kind: str, key: str):
        key = self._normalize_key(key)
        if not key:
            return
        if kind == "step":
            nodes = self._step_nodes.get(key, [])
        else:
            nodes = self._transition_nodes.get(key, [])
        if not nodes:
            return
        if kind == "transition":
            # Only flash transition right before the next step, not immediately.
            self._pending_transition_nodes = nodes
            return
        # Step event
        self._highlight_token += 1
        token = self._highlight_token
        pending = self._pending_transition_nodes
        self._pending_transition_nodes = []
        if pending:
            # Briefly show the transition, then move to the step.
            self._reset_node_styles()
            self._highlight_nodes(pending)
            self._last_highlight_kind = "transition"
            QTimer.singleShot(160, lambda: self._flash_transition_then_step(token, nodes))
            return
        # No pending transition: highlight step immediately.
        self._reset_node_styles()
        self._highlight_nodes(nodes)
        self._last_highlight_kind = "step"

    def _highlight_init(self):
        if not self._init_nodes:
            return
        self._reset_node_styles()
        self._highlight_nodes(self._init_nodes)

    def _highlight_end(self):
        if not self._end_nodes:
            return
        self._reset_node_styles()
        self._highlight_nodes(self._end_nodes)

    def _on_exec_finished(self):
        self._highlight_end()

    def _add_draggable_node_rect(self, rect: QRectF, pen: QPen, brush: QBrush) -> DraggableNodeItem:
        item = DraggableNodeItem(QRectF(0, 0, rect.width(), rect.height()))
        item.setPen(pen)
        item.setBrush(brush)
        item.setPos(rect.left(), rect.top())
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.scene.addItem(item)
        return item

    def _draw_node(self, row: dict, rect: QRectF):
        kind = str(row.get("kind", ""))
        if kind.lower() == "transition":
            node_item = self._add_draggable_node_rect(rect, self._pen_trans, self._brush_trans)
            self._register_node(row, node_item)
            cond = str(row.get("condition", "")).strip()
            cond = re.sub(r"\bStep\s+([^\s]+)", lambda m: f"Step\u00A0{m.group(1)}", cond)
            cond = re.sub(r"\s+is\s+", "\u00A0is\u00A0", cond)
            if cond:
                txt = QGraphicsTextItem(cond, node_item)
                txt.setFont(self._font_step)
                txt.setTextWidth(100)
                opt = txt.document().defaultTextOption()
                # Use word-boundary wrapping so "Step <id>" stays together.
                opt.setWrapMode(QTextOption.WrapMode.WordWrap)
                txt.document().setDefaultTextOption(opt)
                txt.setDefaultTextColor(QColor("#f9f9f9"))
                txt.setPos(node_item.rect().width() + 12, node_item.rect().height() / 2 - 10)
            return node_item
        else:
            node_item = self._add_draggable_node_rect(rect, self._pen_step, self._brush_step)
            self._register_node(row, node_item)
            seq = row.get("seq")
            if seq == self._start_step_seq:
                label = "Init"
                self._init_nodes.append(node_item)
            elif seq == self._end_step_seq:
                label = "End"
                self._end_nodes.append(node_item)
            else:
                name = str(row.get("name", "")).strip()
                proc = str(row.get("procedure", "")).strip()
                label = name if not proc else f"{name}\nProc: {proc}"
            txt = QGraphicsTextItem(label, node_item)
            txt.setFont(self._font_step)
            txt.setTextWidth(node_item.rect().width() - 16)
            opt = txt.document().defaultTextOption()
            opt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            opt.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            txt.document().setDefaultTextOption(opt)
            txt.setDefaultTextColor(QColor("#ffffff"))
            br = txt.boundingRect()
            txt.setPos(
                node_item.rect().width() / 2 - br.width() / 2,
                node_item.rect().height() / 2 - br.height() / 2,
            )
            return node_item

    def _draw_arrow_orthogonal(self, start_node: DraggableNodeItem, end_node: DraggableNodeItem):
        edge = SFCEdge(start_node=start_node, end_node=end_node, scene=self.scene, pen=self._pen_line)
        start_node.add_edge(edge)
        end_node.add_edge(edge)
        edge.update()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_to_width_80)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_zoom_controls()
        # Keep initial view scale consistent with viewport size.
        self._fit_to_width_80()
