# src/frontend/Home.py
import os
import shutil
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTableWidgetItem, QProgressBar, QLabel
)
from qfluentwidgets import (
    CardWidget,
    PushButton,
    SubtitleLabel,
    BodyLabel,
    TableWidget,
    PrimaryPushButton,
    InfoBar,
    InfoBarPosition
)

from .Workers import Worker

class HomePage(QWidget):
    # 定义自定义信号：用于向 MainWindow 发送解析出来的 list[Pea]
    data_ready_signal = pyqtSignal(list)
    sfc_ready_signal = pyqtSignal(list)

    def __init__(self, log_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("home_page")

        self.log_callback = log_callback
        self.selected_file = ""
        self.selected_files = []
        self.last_run_has_aml = False
        self.last_mtp_files = []
        self.last_recipe_files = []

        # --------------------------------------------------
        # Artifact directory (project-root based)
        # --------------------------------------------------
        project_root = os.path.abspath(os.getcwd())
        self.artifact_dir = os.path.join(
            project_root, "artifacts"
        )
        os.makedirs(self.artifact_dir, exist_ok=True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # ---------- Title ----------
        layout.addWidget(SubtitleLabel("Recipol File Manager", self))
        layout.addWidget(
            BodyLabel("Recipes (.xml) and MTP files (.aml) are grouped below.", self)
        )

        # ---------- Import ----------
        card = CardWidget(self)
        card_layout = QHBoxLayout(card)

        btn_import = PushButton("Import File", self)
        btn_import.clicked.connect(self.import_file)
        # card_layout.addWidget(btn_import)
        # card_layout.addStretch(1)

        self.btn_delete = PushButton("Delete Selected", self)
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_selected_file)

        self.btn_reset_selection = PushButton("Reset Selection", self)
        self.btn_reset_selection.setEnabled(False)
        self.btn_reset_selection.clicked.connect(self.reset_selection)

        card_layout.addWidget(btn_import)
        card_layout.addWidget(self.btn_delete)
        card_layout.addWidget(self.btn_reset_selection)
        card_layout.addStretch(1)


        layout.addWidget(card)

        # ---------- Table ----------
        self.table = TableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Type", "File"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(TableWidget.SelectionMode.MultiSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.table, 1)

        # ---------- Selected ----------
        self.lbl_selected = BodyLabel("Selected: None", self)
        self.lbl_selected.setStyleSheet("font-weight: bold; color: #ffffff;")
        # self.lbl_selected.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_selected)

        # ---------- Run ----------
        self.btn_run = PrimaryPushButton("Inspect", self)
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self.run_worker)
        layout.addWidget(self.btn_run)

        self.pbar = QProgressBar(self)
        self.pbar.setTextVisible(False)

        self.pbar_percent = QLabel("0%", self)
        self.pbar_percent.setStyleSheet("color: white;")
        self.pbar_percent.setFixedWidth(40)
        self.pbar_percent.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        pbar_row = QHBoxLayout()
        pbar_row.setContentsMargins(0, 0, 0, 0)
        pbar_row.setSpacing(8)
        pbar_row.addWidget(self.pbar, 1)
        pbar_row.addWidget(self.pbar_percent)
        layout.addLayout(pbar_row)

        # Initial scan
        self.scan_artifact_dir()

    # ------------------------------------------------------------------
    # Scan & Group
    # ------------------------------------------------------------------
    def scan_artifact_dir(self):
        self.table.setRowCount(0)

        recipes = []
        mtps = []

        for name in sorted(os.listdir(self.artifact_dir)):
            full = os.path.join(self.artifact_dir, name)
            if not os.path.isfile(full):
                continue

            if name.lower().endswith(".xml"):
                recipes.append(full)
            elif name.lower().endswith(".aml"):
                mtps.append(full)

        if recipes:
            self.add_group_header("Recipe Files")
            for f in recipes:
                self.add_file_row("Recipe", f)

            # Add spacing after group
            self.add_empty_row()

        if mtps:
            self.add_group_header("MTP Files")
            for f in mtps:
                self.add_file_row("MTP", f)

            # Add spacing after group
            self.add_empty_row()

        self.log_callback(
            f"Scanned Artifact: {len(recipes)} recipes, {len(mtps)} MTP files"
        )

    # ------------------------------------------------------------------
    # Table Helpers
    # ------------------------------------------------------------------
    def add_group_header(self, title):
        row = self.table.rowCount()
        self.table.insertRow(row)

        item = QTableWidgetItem(title)
        item.setFlags(Qt.ItemFlag.NoItemFlags)

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        item.setFont(font)
        item.setBackground(QColor("#2d2d2d"))
        item.setForeground(QColor("#ffffff"))

        self.table.setItem(row, 0, item)
        self.table.setSpan(row, 0, 1, 2)
        self.table.setRowHeight(row, 28)

    def add_file_row(self, ftype, path):
        row = self.table.rowCount()
        self.table.insertRow(row)

        type_item = QTableWidgetItem(ftype)
        type_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 0, type_item)

        file_item = QTableWidgetItem(os.path.basename(path))
        file_item.setToolTip(path)  # Full path tooltip
        file_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        file_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 1, file_item)

        self.table.setRowHeight(row, 24)

    def add_empty_row(self):
        """Add a small spacer row for visual separation."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 8)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------
    def import_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Files",
            "",
            "All Supported Files (*.xml *.aml);;XML Files (*.xml);;AML Files (*.aml);;All Files (*)"
        )

        if not files:
            return

        success_count = 0
        fail_count = 0

        for src in files:
            dst = os.path.join(self.artifact_dir, os.path.basename(src))

            try:
                shutil.copy2(src, dst)
                self.log_callback(f"Imported: {dst}")
                success_count += 1
            except Exception as e:
                self.log_callback(f"Failed to import {src}: {e}")
                fail_count += 1

        # 刷新表格
        self.scan_artifact_dir()

        # 统一提示
        if success_count > 0:
            InfoBar.success(
                title="Import Completed",
                content=f"{success_count} file(s) imported successfully.",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )

        if fail_count > 0:
            InfoBar.error(
                title="Import Issues",
                content=f"{fail_count} file(s) failed to import. See log for details.",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )


    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def on_selection_changed(self):
        items = self.table.selectedItems()
        if not items:
            self.selected_file = ""
            self.selected_files = []
            self.lbl_selected.setText("Selected: None")
            self.btn_run.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_reset_selection.setEnabled(False)
            return

        # 收集所有选中的真实文件（忽略组标题和空行）
        selected_files = []
        for i in range(0, len(items), self.table.columnCount()):
            if items[i].flags() & Qt.ItemFlag.ItemIsSelectable:
                selected_files.append(items[i+1].text())

        if not selected_files:
            self.selected_file = ""
            self.selected_files = []
            self.lbl_selected.setText("Selected: None")
            self.btn_run.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_reset_selection.setEnabled(False)
            return

        self.selected_files = selected_files  # 保存所有选中文件
        self.lbl_selected.setText(f"Selected: {len(selected_files)} file(s)")
        # self.btn_run.setEnabled(len(selected_files) == 1)  # 运行Worker只允许单选
        self.btn_run.setEnabled(True)    # 多选时也可运行 Worker
        self.btn_delete.setEnabled(True)
        self.btn_reset_selection.setEnabled(True)


    def reset_selection(self):
        self.table.clearSelection()
        self.selected_file = ""
        self.selected_files = []
        self.lbl_selected.setText("Selected: None")
        self.set_progress(0)
        self.btn_run.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_reset_selection.setEnabled(False)


    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_selected_file(self):
        if not hasattr(self, "selected_files") or not self.selected_files:
            return

        deleted_count = len(self.selected_files)
        failed = []
        for fname in self.selected_files:
            full_path = os.path.join(self.artifact_dir, fname)
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
                else:
                    failed.append(fname)
            except Exception:
                failed.append(fname)

        # 更新表格
        self.scan_artifact_dir()
        self.reset_selection()

        if failed:
            InfoBar.error(
                title="Delete Failed",
                content=f"Failed to delete: {', '.join(failed)}",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )
        else:
            InfoBar.success(
                title="Deleted",
                content=f"Deleted {deleted_count} file(s)",
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )


    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------
    # def run_worker(self):
    #     if not self.selected_files:
    #         return

    #     self.btn_run.setEnabled(False)
    #     self.pbar.setValue(0)

    #     # 将 Worker 修改为接收文件列表
    #     full_paths = [os.path.join(self.artifact_dir, f) for f in self.selected_files]
    #     # self.worker = Worker(self.selected_files)  
    #     self.worker = Worker(full_paths)
    #     self.worker.log_signal.connect(self.log_callback)
    #     self.worker.progress_signal.connect(self.pbar.setValue)
    #     self.worker.finished_signal.connect(self.on_finished)
    #     self.worker.start()     #执行Worker.py里的run()

    # Code/GUI/Home.py

    def run_worker(self):
        if not self.selected_files:
            return

        self.btn_run.setEnabled(False)
        self.set_progress(0)

        # 【核心改动】：在这里进行过滤，只提取以 .aml 结尾的文件
        # 这样只有 MTP 文件会被送入后端 getMtps 函数
        aml_files = [
            os.path.join(self.artifact_dir, f) 
            for f in self.selected_files 
            if f.lower().endswith('.aml')
        ]
        self.last_run_has_aml = len(aml_files) > 0
        self.last_mtp_files = list(aml_files)
        
        # 获取非 aml 文件（如 .xml），用于日志记录
        recipe_files = [
            os.path.join(self.artifact_dir, f)
            for f in self.selected_files
            if f.lower().endswith('.xml')
        ]

        self.last_recipe_files = list(recipe_files)
        unsupported_files = [
            f for f in self.selected_files
            if not (f.lower().endswith('.aml') or f.lower().endswith('.xml'))
        ]

        # 如果有非 MTP 文件，在日志里打个招呼
        if unsupported_files:
            self.log_callback(f"Skipping unsupported files: {', '.join(unsupported_files)}")

        # 如果连一个 .aml 都没有选，直接结束
        if not aml_files and not recipe_files:
            self.log_callback("No .aml or .xml files selected. Task aborted.")
            self.btn_run.setEnabled(True)
            return

        # 将过滤后的 aml_files 传给 Worker
        self.worker = Worker(mtp_files=aml_files, recipe_files=recipe_files)
        self.worker.log_signal.connect(self.log_callback)
        self.worker.progress_signal.connect(self.set_progress)
        self.worker.finished_signal.connect(self.on_finished)       # 一旦 finished_signal 被发射（emit），请立刻自动执行 on_finished 这个函数。
        self.worker.start()

    def set_progress(self, value: int):
        value = max(0, min(100, int(value)))
        self.pbar.setValue(value)
        self.pbar_percent.setText(f"{value}%")

    def on_finished(self):
        self.btn_run.setEnabled(True)

        parsed_mtps = getattr(self.worker, 'mtp_results', [])       # getattr(object, "属性名", 默认值)，取object.属性名
        # print(parsed_mtps)

        failed_files = getattr(self.worker, 'failed_files', [])
        sfc_results = getattr(self.worker, 'sfc_results', [])
        failed_recipe_files = getattr(self.worker, 'failed_recipe_files', [])
        total_mtp_files = getattr(self.worker, 'total_mtp_files', 0)
        self.data_ready_signal.emit(parsed_mtps)
        self.sfc_ready_signal.emit(sfc_results)

        if total_mtp_files == 0:
            if sfc_results:
                self.log_callback(f"SFC generated with {len(sfc_results)} elements.")
            if failed_recipe_files:
                failed_recipe_names = [os.path.basename(f) for f in failed_recipe_files]
                warn_text = f"Failed to generate SFC from: {', '.join(failed_recipe_names)}"
                self.log_callback(f"Warning: {warn_text}")
                InfoBar.warning(
                    title="Warning",
                    content=warn_text,
                    isClosable=True,
                    duration=5000,
                    parent=self.window(),
                    position=InfoBarPosition.TOP_RIGHT
                )
            return

        if failed_files and parsed_mtps:
            failed_names = [os.path.basename(f) for f in failed_files]
            if len(failed_names) == 1:
                warn_text = f"{failed_names[0]} has no data parsed to display."
            else:
                warn_text = f"{', '.join(failed_names)} have no data parsed to display."

            self.log_callback(f"Warning: {warn_text}")
            InfoBar.warning(
                title="Warning",
                content=warn_text,
                isClosable=True,
                duration=5000,
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )
        elif parsed_mtps:
            self.log_callback(f"Successfully sent {len(parsed_mtps)} MTPs to Viewer.")
            InfoBar.success(
                title="Done",
                content="Files imported successfully.",
                isClosable=True,
                duration=3000,
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )
        else:
            self.log_callback("Error: No MTP file has data parsed to display.")
            InfoBar.error(
                title="Error",
                content="No MTP file has data parsed to display.",
                isClosable=True,
                duration=5000,
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )

        if failed_recipe_files:
            failed_recipe_names = [os.path.basename(f) for f in failed_recipe_files]
            warn_text = f"Failed to generate SFC from: {', '.join(failed_recipe_names)}"
            self.log_callback(f"Warning: {warn_text}")
            InfoBar.warning(
                title="Warning",
                content=warn_text,
                isClosable=True,
                duration=5000,
                parent=self.window(),
                position=InfoBarPosition.TOP_RIGHT
            )
            
        
