"""Application colour palettes and shared widget styling."""

THEMES = {
    "Dark": {
        "background": "#111722", "sidebar": "#151D2A", "surface": "#1A2432",
        "surface_alt": "#202C3B", "text": "#E9EEF5", "muted": "#9AA8B8",
        "accent": "#7A8CFF", "accent_text": "#101426", "border": "#2B394B",
        "hover": "#253247", "selection": "#303A62",
    },
    "Light": {
        "background": "#E9EDF2", "sidebar": "#E2E7ED", "surface": "#F0F2F5",
        "surface_alt": "#E6EAF0", "text": "#202A38", "muted": "#657386",
        "accent": "#5269D8", "accent_text": "#FFFFFF", "border": "#D2D9E2",
        "hover": "#DDE3EA", "selection": "#D6DDF4",
    },
    "Executive": {
        "background": "#171716", "sidebar": "#1C1C1A", "surface": "#242321",
        "surface_alt": "#2C2A27", "text": "#F1EEE7", "muted": "#B0AA9E",
        "accent": "#C8A96B", "accent_text": "#19160F", "border": "#393630",
        "hover": "#34312A", "selection": "#49402E",
    },
    "Calm": {
        "background": "#EAEAF0", "sidebar": "#E2E2EB", "surface": "#F0F0F5",
        "surface_alt": "#E5E5ED", "text": "#292B3B", "muted": "#6B6E82",
        "accent": "#7774C9", "accent_text": "#FFFFFF", "border": "#D2D2DF",
        "hover": "#DDDEE8", "selection": "#D8D8EF",
    },
}


def stylesheet(theme="Dark", density="Comfortable", font="Segoe UI", font_size=10):
    colors = THEMES.get(theme, THEMES["Dark"])
    pad = "7px 12px" if density == "Compact" else "9px 14px"
    return f"""
        QMainWindow {{ background: {colors['background']}; }}
        QWidget {{ background-color: transparent; color: {colors['text']};
            font-family: "{font}"; font-size: {font_size}pt; }}
        QWidget#appRoot {{ background: {colors['background']}; }}
        QStackedWidget#appPages {{ background: {colors['background']}; }}
        #sidebar {{ background: {colors['sidebar']}; border-right: 1px solid {colors['border']}; }}
        #topbar {{ background: {colors['sidebar']}; border-bottom: 1px solid {colors['border']}; }}
        #logo, #topbarTitle, #pageTitle {{ color: {colors['text']}; }}
        #logo {{ font-size: {round(font_size * 1.75)}pt; font-weight: 700; }}
        #logoSubtitle, #statusText, #pageSubtitle, #mutedText {{ color: {colors['muted']}; }}
        #topbarTitle {{ font-size: {round(font_size * 1.05)}pt; font-weight: 650; }}
        #pageTitle {{ font-size: {round(font_size * 1.9)}pt; font-weight: 700; }}
        #pageSubtitle, #mutedText {{ font-size: {round(font_size * 0.95)}pt; }}
        #sectionTitle {{ color: {colors['text']}; font-size: {round(font_size * 1.08)}pt; font-weight: 650; }}
        #settingsHeading {{ color: {colors['text']}; font-size: {round(font_size * 1.45)}pt; font-weight: 700; }}
        #statHeading {{ color: {colors['muted']}; font-size: {round(font_size * 0.85)}pt; font-weight: 600; }}
        #statValue {{ color: {colors['text']}; font-size: {round(font_size * 1.9)}pt; font-weight: 700; }}
        #navButton {{ background: transparent; color: {colors['muted']}; border: 0;
            border-radius: 8px; text-align: left; padding: {pad}; }}
        #navButton:hover {{ background: {colors['hover']}; color: {colors['text']}; }}
        #navButton[active="true"] {{ background: {colors['selection']}; color: {colors['text']};
            border-left: 3px solid {colors['accent']}; }}
        #panel, #statCard, #settingsCard, #aboutCard {{ background: {colors['surface']};
            border: 1px solid {colors['border']}; border-radius: 12px; }}
        #settingsLabel {{ color: {colors['text']}; font-weight: 600; }}
        #aboutTitle {{ color: {colors['text']}; font-size: {round(font_size * 1.25)}pt; font-weight: 700; }}
        #aboutStatus {{ color: {colors['accent']}; font-weight: 650; }}
        QPushButton {{ background: {colors['surface_alt']}; color: {colors['text']};
            border: 1px solid {colors['border']}; border-radius: 8px; padding: {pad}; font-weight: 550; }}
        QPushButton:hover {{ background: {colors['hover']}; border-color: {colors['accent']}; }}
        QPushButton:pressed {{ background: {colors['selection']}; }}
        QPushButton:disabled {{ color: {colors['muted']}; }}
        QPushButton#accentButton {{ background: {colors['accent']}; color: {colors['accent_text']};
            border: 0; font-weight: 650; }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{
            background: {colors['surface_alt']}; color: {colors['text']};
            border: 1px solid {colors['border']}; border-radius: 8px; padding: {pad};
            selection-background-color: {colors['selection']}; }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
        QPlainTextEdit:focus {{ border-color: {colors['accent']}; }}
        QComboBox QAbstractItemView {{ background: {colors['surface']}; color: {colors['text']};
            border: 1px solid {colors['border']}; selection-background-color: {colors['selection']};
            outline: 0; }}
        QListWidget, QTableWidget, QTreeWidget {{ background: {colors['surface']};
            alternate-background-color: {colors['surface_alt']}; color: {colors['text']};
            border: 1px solid {colors['border']}; border-radius: 9px;
            gridline-color: {colors['border']}; selection-background-color: {colors['selection']}; }}
        QTableWidget::item {{ color: {colors['text']}; padding: 6px; border: 0; }}
        QTableWidget::item:hover {{ background: {colors['hover']}; }}
        QHeaderView::section {{ background: {colors['surface']}; color: {colors['muted']};
            border: 0; border-bottom: 1px solid {colors['border']}; padding: {pad}; font-weight: 650; }}
        QScrollArea {{ background: transparent; border: 0; }}
        QScrollBar:vertical {{ background: transparent; width: 9px; margin: 3px; }}
        QScrollBar::handle:vertical {{ background: {colors['border']}; border-radius: 4px; min-height: 24px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QCheckBox {{ spacing: 8px; }}
        QToolTip {{ color: {colors['text']}; background: {colors['surface']};
            border: 1px solid {colors['border']}; padding: 5px; }}
        QDialog, QMessageBox {{ background: {colors['background']}; color: {colors['text']}; }}
    """


def apply_theme(app, settings, window=None):
    base_size = int(settings.get("font_size", 10))
    scale = int(settings.get("interface_scale", 100))
    effective_size = max(8, min(20, round(base_size * scale / 100)))
    app.setStyleSheet(stylesheet(
        settings.get("theme", "Dark"),
        settings.get("density", "Comfortable"),
        settings.get("font", "Segoe UI"),
        effective_size,
    ))
    return "Standard window appearance is active."