# src/frontend/MTPViewer.py
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTreeWidgetItem
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    ComboBox, 
    TreeWidget, 
    TitleLabel, 
    SubtitleLabel, 
    CardWidget,
    FluentIcon
)

class MTPViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MTPViewer")
        
        # 存储原始数据 list[Pea]
        self.mtp_results = []

        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # 1. 标题区域
        self.title_label = TitleLabel("MTP Viewer", self)
        self.sub_title = SubtitleLabel("View details of parsed Services, Procedures, and Parameters", self)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.sub_title)

        # 2. 选择区域 (使用 CardWidget 包裹 ComboBox 显得更美观)
        self.selection_card = CardWidget(self)
        self.card_layout = QHBoxLayout(self.selection_card)
        
        self.combo_box = ComboBox(self)
        self.combo_box.setPlaceholderText("Select an MTP file on the Homepage to view")
        self.combo_box.setMinimumWidth(300)
        self.combo_box.currentIndexChanged.connect(self._on_mtp_changed)
        
        self.card_layout.addWidget(self.combo_box)
        self.card_layout.addStretch(1)
        self.main_layout.addWidget(self.selection_card)

        # 3. 树形展示区域
        self.tree_widget = TreeWidget(self)
        # 设置表头
        self.tree_widget.setHeaderLabels(["Hierarchy (Name)", "ID", "Type", "Default Value", "Low Limit", "High Limit", "Unit"])
        self.tree_widget.setColumnWidth(0, 250)
        self.tree_widget.setColumnWidth(1, 280)
        self.tree_widget.setColumnWidth(2, 100)
        self.tree_widget.setColumnWidth(3, 100)
        self.tree_widget.setColumnWidth(4, 70)
        self.tree_widget.setColumnWidth(5, 80)
        self.tree_widget.setColumnWidth(6, 100)
        
        self.main_layout.addWidget(self.tree_widget, 1) # 1 表示占用剩余所有空间

    def update_data(self, mtps: list):
        """
        供 MainWindow 调用，更新页面数据
        :param mtps: list[Pea] 后端解析出来的对象列表
        """
        self.mtp_results = mtps
        
        # 阻止信号触发，避免在 clear 时由于索引变化导致报错
        self.combo_box.blockSignals(True)
        self.combo_box.clear()
        
        if not mtps:
            self.combo_box.setPlaceholderText("No valid MTP data found")
            self.tree_widget.clear()
            self.combo_box.blockSignals(False)
            return

        # 填充下拉列表
        for pea in mtps:
            # 优先显示 pea.name，如果没有则显示文件名或 ID
            display_name = getattr(pea, 'name', 'Unknown MTP')
            self.combo_box.addItem(display_name, icon=FluentIcon.APPLICATION)
            
        self.combo_box.blockSignals(False)
        
        # 默认选中第一个
        if self.combo_box.count() > 0:
            self.combo_box.setCurrentIndex(0)
            self._on_mtp_changed(0)

    def _on_mtp_changed(self, index):
        """下拉框切换时刷新树形图"""
        if index < 0 or index >= len(self.mtp_results):
            return

        self.tree_widget.clear()
        selected_mtp = self.mtp_results[index]

        column_count = self.tree_widget.columnCount()

        # 遍历层级结构并填充树
        # 1层: Service (m.servs)
        for s in getattr(selected_mtp, 'servs', []):
            s_item = QTreeWidgetItem(self.tree_widget, [s.name, s.id, "Service", "", "", "", ""])
            s_item.setIcon(0, FluentIcon.ROBOT.icon()) 

            s_item.setFlags(s_item.flags() | Qt.ItemFlag.ItemIsEditable)

            s_item.setExpanded(True)

            # 2层: Procedure (s.procs)
            for p in getattr(s, 'procs', []):
                p_item = QTreeWidgetItem(s_item, [p.name, p.id, "Procedure", "", "", "",""])
                p_item.setIcon(0, FluentIcon.SETTING.icon())

                p_item.setFlags(p_item.flags() | Qt.ItemFlag.ItemIsEditable)

                # p_item.setExpanded(True)

                # 3层: Parameter (p.params)
                for pa in getattr(p, 'params', []):
                    # Show refined parameter type from AML RefBaseSystemUnitPath when available.
                    parameter_type = getattr(pa, 'parameter_type', None) or "Parameter"
                    # 将参数的详细信息填入列
                    pa_item = QTreeWidgetItem(p_item, [
                        pa.name, 
                        pa.id,
                        parameter_type,
                        str(getattr(pa, 'default', '')), 
                        str(pa.paramElem.get('VSclMin', {}).get('Default', '')),
                        str(pa.paramElem.get('VSclMax', {}).get('Default', '')),
                        str(getattr(pa, 'unit', ''))
                    ])
                    pa_item.setIcon(0, FluentIcon.STOP_WATCH.icon())
                    for i in range(2, column_count):
                        pa_item.setTextAlignment(i, Qt.AlignmentFlag.AlignCenter)
                    pa_item.setFlags(pa_item.flags() | Qt.ItemFlag.ItemIsEditable)

                    # pa_item.setExpanded(False)

        # # 自动展开所有节点
        # self.tree_widget.expandAll()
