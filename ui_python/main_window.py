from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from modules.backend_connector import BackendConnector
from modules.lookups import LookupsManager

from widgets.home import HomeWidget
from widgets.overview import OverviewWidget
from widgets.planner import PlannerWidget
from widgets.calendar import CalendarWidget
from widgets.habits import HabitsWidget
from widgets.goals import GoalsWidget
from widgets.settings import SettingsWidget
from widgets.gamification import GamificationWidget
from widgets.pomodoro import PomodoroWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusBuddy")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #F7F7F5;") 
        
        # 1. API & Data
        self.api = BackendConnector()
        self.lookups = LookupsManager(self.api)
        
        # 2. Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 3. Header
        self.setup_header()
        
        # 4. Tabs Setup
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: transparent; color: #666; padding: 10px 20px;
                font-weight: bold; font-size: 12px; border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected { color: #383838; border-bottom: 2px solid #AFAE9D; }
            QTabBar::tab:hover { color: #383838; }
        """)
        
        self.planner_widget = PlannerWidget(self)
        self.pomodoro_widget = PomodoroWidget(self)
        self.habits_widget = HabitsWidget(self)
        self.calendar_widget = CalendarWidget(self)
        self.goals_widget = GoalsWidget(self)
        self.overview_widget = OverviewWidget(self)
        self.gamification_widget = GamificationWidget(self)
        self.settings_widget = SettingsWidget(self)
        
        self.home_widget = HomeWidget(self)
        
        self.tabs.addTab(self.home_widget, "HOME")          
        self.tabs.addTab(self.planner_widget, "PLANNER")    
        self.tabs.addTab(self.pomodoro_widget, "FOCUS")     
        self.tabs.addTab(self.habits_widget, "HABITS")      
        self.tabs.addTab(self.calendar_widget, "CALENDAR")  
        self.tabs.addTab(self.goals_widget, "GOALS")        
        self.tabs.addTab(self.overview_widget, "ANALYTICS") 
        self.tabs.addTab(self.gamification_widget, "PROFILE") 
        self.tabs.addTab(self.settings_widget, "SETTINGS")  
        
        self.main_layout.addWidget(self.tabs)
        
        self.refresh_all()

    def setup_header(self):
        h = QFrame()
        h.setObjectName("GlobalHeader")
        h.setFixedHeight(50) 
        h.setStyleSheet("#GlobalHeader { background-color: white; border-bottom: 1px solid #E0E0E0; }")
        hl = QHBoxLayout(h); hl.setContentsMargins(15, 5, 15, 5) 
        
        # Date
        date_str = datetime.now().strftime("%A, %d %B").upper()
        date_lbl = QLabel(date_str)
        date_lbl.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        date_lbl.setStyleSheet("color: #888; letter-spacing: 1px;")
        hl.addWidget(date_lbl)
        hl.addStretch()
        
        # Profile
        self.profile_container = QWidget()
        pc_layout = QHBoxLayout(self.profile_container); pc_layout.setContentsMargins(0, 0, 0, 0); pc_layout.setSpacing(10)
        
        self.lvl_lbl = QLabel("LVL 1")
        self.lvl_lbl.setStyleSheet("background-color: #383838; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        pc_layout.addWidget(self.lvl_lbl)
        
        xp_wid = QWidget(); xp_layout = QVBoxLayout(xp_wid); xp_layout.setContentsMargins(0,5,0,5); xp_layout.setSpacing(1)
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedWidth(100); self.xp_bar.setFixedHeight(6); self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet("QProgressBar { border: none; background-color: #F0F0F0; border-radius: 3px; } QProgressBar::chunk { background-color: #6C5CE7; border-radius: 3px; }")
        self.xp_bar.setToolTip("XP Progress")
        xp_layout.addWidget(self.xp_bar)
        pc_layout.addWidget(xp_wid)
        
        self.avatar_lbl = QLabel("😎")
        self.avatar_lbl.setFont(QFont("Segoe UI Emoji", 18))
        self.avatar_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        pc_layout.addWidget(self.avatar_lbl)
        hl.addWidget(self.profile_container)
        self.main_layout.addWidget(h)

    def refresh_all(self):
        """ОНОВЛЮЄ АБСОЛЮТНО ВСЕ"""
        self.lookups.load_all() 
        
        user = self.api.get_user()
        if user:
            lvl = int(user.get('level', 1))
            xp = int(user.get('xp', 0))
            avatar = user.get('avatar', '😎')
            xp_needed = lvl * 100
            self.lvl_lbl.setText(f"LVL {lvl}")
            self.xp_bar.setMaximum(xp_needed)
            self.xp_bar.setValue(xp)
            self.xp_bar.setToolTip(f"{xp} / {xp_needed} XP")
            self.avatar_lbl.setText(avatar)

        try: self.planner_widget.refresh_planner() 
        except Exception as e: print(f"Planner error: {e}")
            
        try: self.home_widget.refresh_home()
        except Exception as e: print(f"Home error: {e}")
            
        try: self.overview_widget.refresh_overview()
        except Exception as e: print(f"Overview error: {e}")
            
        try: self.habits_widget.load_habit_grid()
        except Exception as e: print(f"Habits error: {e}")
            
        try: self.calendar_widget.refresh_calendar()
        except Exception as e: print(f"Calendar error: {e}")
            
        try: self.goals_widget.load_goals()
        except Exception as e: print(f"Goals error: {e}")
            
        try: self.settings_widget.refresh_settings()
        except Exception as e: print(f"Settings error: {e}")
            
        try: self.gamification_widget.refresh_profile()
        except Exception as e: print(f"Profile error: {e}")
        
        if hasattr(self.pomodoro_widget, 'refresh_stats'):
             self.pomodoro_widget.refresh_stats()