from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QFrame, QGridLayout, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from charts import PieChart

class DashboardWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        self.layout = QHBoxLayout(content_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # === LEFT PANEL (70%) ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        # 1. KPI Header
        kpi_container = QWidget()
        kpi_layout = QHBoxLayout(kpi_container)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(15)
        
        self.kpi_total = self.create_kpi_card("TOTAL TASKS", "0")
        self.kpi_today = self.create_kpi_card("TODAY", "0")
        self.kpi_overdue = self.create_kpi_card("OVERDUE", "0", is_alert=True)
        self.kpi_done = self.create_kpi_card("DONE", "0", is_success=True)
        
        kpi_layout.addWidget(self.kpi_total)
        kpi_layout.addWidget(self.kpi_today)
        kpi_layout.addWidget(self.kpi_overdue)
        kpi_layout.addWidget(self.kpi_done)
        
        left_layout.addWidget(kpi_container)
        
        # 2. Charts Section
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chart_prio = PieChart()
        c1 = self.create_chart_column("BY PRIORITY", self.chart_prio)
        
        self.chart_stat = PieChart()
        c2 = self.create_chart_column("BY STATUS", self.chart_stat)
        
        self.chart_cat = PieChart()
        c3 = self.create_chart_column("BY CATEGORY", self.chart_cat)

        charts_layout.addWidget(c1)
        charts_layout.addWidget(c2)
        charts_layout.addWidget(c3)
        
        left_layout.addWidget(charts_container)
        left_layout.addStretch()
        
        # === RIGHT PANEL (30%) - SIDEBAR ===
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 20, 15, 20)
        right_layout.setSpacing(15)
        
        # 1. Tasks for Today
        lbl_today = QLabel("TASKS FOR TODAY")
        lbl_today.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        lbl_today.setStyleSheet("color: #E0C068;") 
        right_layout.addWidget(lbl_today)
        
        self.list_today = QListWidget()
        self.list_today.setFrameShape(QFrame.Shape.NoFrame)
        self.list_today.setStyleSheet("background: transparent; font-size: 13px;")
        self.list_today.setMaximumHeight(150) 
        right_layout.addWidget(self.list_today)

        line1 = QFrame(); line1.setFrameShape(QFrame.Shape.HLine); line1.setStyleSheet("color: #E0E0E0;")
        right_layout.addWidget(line1)
        
        # 2. Tasks for Tomorrow
        lbl_tom = QLabel("TASKS FOR TOMORROW")
        lbl_tom.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        lbl_tom.setStyleSheet("color: #4A4A4A;")
        right_layout.addWidget(lbl_tom)
        
        self.list_tomorrow = QListWidget()
        self.list_tomorrow.setFrameShape(QFrame.Shape.NoFrame)
        self.list_tomorrow.setStyleSheet("background: transparent; font-size: 13px;")
        self.list_tomorrow.setMaximumHeight(150)
        right_layout.addWidget(self.list_tomorrow)
        
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine); line2.setStyleSheet("color: #E0E0E0;")
        right_layout.addWidget(line2)

        # 3. Overdue Tasks
        lbl_over = QLabel("OVERDUE TASKS")
        lbl_over.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        lbl_over.setStyleSheet("color: #D45D5D;")
        right_layout.addWidget(lbl_over)
        
        self.list_overdue = QListWidget()
        self.list_overdue.setFrameShape(QFrame.Shape.NoFrame)
        self.list_overdue.setStyleSheet("background: transparent; font-size: 13px;")
        right_layout.addWidget(self.list_overdue)

        right_layout.addStretch()

        self.layout.addWidget(left_panel, 70)
        self.layout.addWidget(right_panel, 30)
        
        main_scroll.setWidget(content_widget)
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0,0,0,0)
        wrapper_layout.addWidget(main_scroll)

    def create_kpi_card(self, title, value, is_alert=False, is_success=False):
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedHeight(100)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Oswald", 24, QFont.Weight.Bold))
        if is_alert: val_lbl.setStyleSheet("color: #D45D5D;")
        elif is_success: val_lbl.setStyleSheet("color: #7FB06F;")
        else: val_lbl.setStyleSheet("color: #383838;")
            
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Inter", 9))
        title_lbl.setStyleSheet("color: #888;")
        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)
        return card

    def create_chart_column(self, title, chart_widget):
        container = QFrame()
        container.setObjectName("Card")
        l = QVBoxLayout(container)
        header = QLabel(title)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Oswald", 11, QFont.Weight.Bold))
        header.setStyleSheet("color: #4A4A4A; margin-bottom: 10px;")
        l.addWidget(header)
        l.addWidget(chart_widget)
        return container

    def refresh_dashboard(self):
        stats = self.api.get_dashboard()
        if stats:
  
            def set_val(card, val):
                # Layout items: 0=Value, 1=Title
                item = card.layout().itemAt(0).widget()
                if isinstance(item, QLabel):
                    item.setText(str(val))

            set_val(self.kpi_total, stats.get('total_active', 0))
            set_val(self.kpi_today, stats.get('today_count', 0))
            set_val(self.kpi_overdue, stats.get('overdue_count', 0))
            set_val(self.kpi_done, stats.get('done_total', 0))

        # 2. Update Charts
        self.chart_prio.plot(self.api.get_chart_data("priority"), "")
        self.chart_stat.plot(self.api.get_chart_data("status"), "")
        self.chart_cat.plot(self.api.get_chart_data("category"), "")

        # 3. Update Sidebar - TODAY
        self.list_today.clear()
        today_tasks = self.api.get_today_tasks()
        if not today_tasks:
            item = QListWidgetItem("You are free today!")
            item.setForeground(QColor("#7FB06F"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_today.addItem(item)
        else:
            for t in today_tasks:
                item = QListWidgetItem(f"• {t['title']}")
                item.setForeground(QColor("#383838"))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.list_today.addItem(item)

        # 4. Update Sidebar - TOMORROW
        self.list_tomorrow.clear()
        tomorrow_tasks = self.api.get_tomorrow_tasks()
        if not tomorrow_tasks:
            item = QListWidgetItem("No tasks for tomorrow :)")
            item.setForeground(QColor("#888"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_tomorrow.addItem(item)
        else:
            for t in tomorrow_tasks:
                item = QListWidgetItem(f"• {t['title']}")
                item.setForeground(QColor("#666"))
                self.list_tomorrow.addItem(item)

        # 5. Update Sidebar - OVERDUE
        self.list_overdue.clear()
        overdue_tasks = self.api.get_overdue_tasks()
        if not overdue_tasks:
             item = QListWidgetItem("No overdue tasks!")
             item.setForeground(QColor("#7FB06F"))
             self.list_overdue.addItem(item)
        else:
            for t in overdue_tasks:
                date_short = t['deadline_date'][5:] 
                item = QListWidgetItem(f"• {t['title']} ({date_short})")
                item.setForeground(QColor("#D45D5D"))
                self.list_overdue.addItem(item)