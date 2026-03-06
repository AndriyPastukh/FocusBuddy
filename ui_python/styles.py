TRACKERY_STYLE = """
/* === GLOBAL === */
QMainWindow, QWidget { 
    background-color: #F7F7F5; /* Digital Paper Beige */
    color: #383838; 
    font-family: 'Segoe UI', sans-serif;
}

/* === HEADER BAR === */
QFrame#GlobalHeader {
    background-color: transparent;
    border-bottom: 2px solid #E0E0E0;
}
QLabel#LogoText {
    font-family: 'Impact', sans-serif; /* Fallback for Oswald */
    font-size: 26px;
    letter-spacing: 2px;
    color: #383838;
    text-transform: uppercase;
}

/* === TABS === */
QTabWidget::pane { border: none; }
QTabBar::tab {
    background: transparent;
    color: #888;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
    text-transform: uppercase;
}
QTabBar::tab:selected {
    color: #383838;
    border-bottom: 3px solid #AFAE9D; /* Taupe */
}

/* === CARDS & PANELS === */
QFrame#Card {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 0px; /* Sharp corners per spec */
}

/* === TABLES === */
QTableWidget, QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    gridline-color: #F0F0F0;
    font-size: 14px;
}
QHeaderView::section {
    background-color: #CFCBC2; /* Light Taupe */
    color: #383838;
    padding: 8px;
    border: none;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 12px;
}

/* === BUTTONS === */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #AFAE9D;
    color: #383838;
    padding: 8px 16px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #F0F0F0;
}
QPushButton#PrimaryBtn {
    background-color: #383838;
    color: #FFFFFF;
    border: 1px solid #383838;
}
QPushButton#PrimaryBtn:hover {
    background-color: #555555;
}
QPushButton#DangerBtn {
    border-color: #D45D5D;
    color: #D45D5D;
}
QPushButton#DangerBtn:hover {
    background-color: #FFF0F0;
}

/* === INPUTS === */
QLineEdit, QDateEdit, QTimeEdit, QComboBox {
    padding: 6px;
    border: 1px solid #CCCCCC;
    background: #FFFFFF;
    selection-background-color: #AFAE9D;
}

/* === KPI STATS === */
QLabel#KpiNum { font-size: 32px; font-weight: bold; color: #383838; }
QLabel#KpiLabel { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
"""