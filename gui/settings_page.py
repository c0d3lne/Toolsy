"""Settings centre and local settings storage for Toolsy."""
import json
import os
import zipfile
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QStackedWidget, QListWidget, QListWidgetItem, QScrollArea,
    QCheckBox, QComboBox, QSpinBox, QFileDialog, QMessageBox, QInputDialog,
)

PROJECT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_PATH / "data"
SETTINGS_FILE = DATA_PATH / "settings.json"
BACKUP_PATH = DATA_PATH / "backups"
VERSION = "1.0"

DEFAULTS = {
    "launch_on_startup": False, "minimise_on_startup": False,
    "minimise_to_tray": False, "remember_last_page": True,
    "confirm_before_closing": False, "confirm_before_deleting": True,
    "confirm_before_clearing": True, "remember_window_size": True,
    "remember_window_position": True, "compact_mode": False,
    "theme": "Dark", "font": "Segoe UI",
    "font_size": 10, "interface_scale": 100, "density": "Comfortable",
    "watch_auto_monitor": False, "watch_check_startup": False,
    "watch_check_new": False, "watch_available_notifications": False,
    "watch_notification_sounds": False, "watch_remember_status": True,
    "watch_keep_history": True, "generator_quantity": 25,
    "generator_category": "4 Letter", "generator_deduplicate": True,
    "generator_ignore_case": True, "generator_preserve_spelling": True,
    "generator_auto_copy": False, "checker_auto_save": False,
    "checker_remember_filters": True, "checker_organise": True,
    "checker_separate_valid": True, "checker_availability": False,
    "import_folder": str(Path.home() / "Downloads"),
    "export_folder": str(Path.home() / "Documents"),
    "import_deduplicate": True, "import_ignore_blank": True,
    "export_format": "TXT", "export_remember_location": True,
    "duplicate_enabled": True, "duplicate_auto": True,
    "duplicate_before_check": True, "duplicate_ignore_case": True,
    "duplicate_preserve_spelling": True, "duplicate_history": True,
    "proxy_enabled": False, "proxy_method": "Direct connection",
    "proxy_protocol": "HTTP", "proxy_auto_select": False,
    "proxy_skip_failed": True, "proxy_test_startup": False,
    "proxy_timeout": 10, "proxy_remember_selection": True,
    "desktop_notifications": False, "in_app_notifications": True,
    "notification_sounds": False, "notify_watch_available": True,
    "notify_proxy_finished": True, "notify_updates": True,
    "notification_history": [], "auto_backups": False,
    "backup_frequency": "Weekly", "enable_update_notifications": True,
    "window_width": 1400, "window_height": 850, "window_x": None,
    "window_y": None, "last_page": 0, "last_backup": "",
}

# key, title, explanation, kind, choices, enabled
CATEGORIES = [
    ("General", "Application behaviour and safety preferences.", [
        ("launch_on_startup", "Launch on Windows startup", "Start Toolsy when you sign in. Off by default.", "bool", None, True),
        ("minimise_on_startup", "Minimise on startup", "Start minimised when startup launch is enabled.", "bool", None, True),
        ("minimise_to_tray", "Minimise to system tray", "Keep the app available in the notification area.", "bool", None, True),
        ("remember_last_page", "Remember last page", "Reopen the last selected sidebar page.", "bool", None, True),
        ("confirm_before_closing", "Confirm before closing", "Ask before the app exits.", "bool", None, True),
        ("confirm_before_deleting", "Confirm before deleting", "Saved preference; existing pages keep their current confirmation prompts.", "bool", None, True),
        ("confirm_before_clearing", "Confirm before clearing data", "Always required for safety and cannot be disabled.", "bool", None, True),
        ("remember_window_size", "Remember window size", "Restore the previous width and height.", "bool", None, True),
        ("remember_window_position", "Remember window position", "Restore position only if it still intersects a connected monitor.", "bool", None, True),
        ("compact_mode", "Compact mode", "Reduce shared control padding and layout spacing.", "bool", None, True),
    ]),
    ("Appearance", "Choose a theme and tune typography and density.", [
        ("theme", "Application Theme", "Apply a coordinated colour palette immediately.", "choice", ["Dark", "Light", "Executive", "Calm"], True),

        ("font", "Application font", "Choose from installed system fonts.", "choice", None, True),
        ("font_size", "Font size", "Base application text size.", "choice", ["Small", "Default", "Comfortable", "Large", "Extra Large"], True),
        ("interface_scale", "Interface scaling", "Adjust the UI scale where Qt supports it; restart may be needed for full effect.", "choice", ["90%", "100%", "110%", "125%", "150%"], True),
        ("density", "Layout density", "Comfortable or compact spacing across shared controls.", "choice", ["Comfortable", "Compact"], True),
    ]),
    ("Watchlist", "Saved preferences for watchlist behaviour. Availability checking is not connected.", [
        ("watch_auto_monitor", "Enable automatic monitoring", "Unavailable: the current validator only checks formatting.", "bool", None, False),
        ("watch_check_startup", "Check watchlist on startup", "Unavailable until a genuine Xbox availability checker exists.", "bool", None, False),
        ("watch_check_new", "Check newly added names", "Unavailable until genuine availability checks are implemented.", "bool", None, False),
        ("watch_available_notifications", "Available-name notifications", "Preference only; no genuine status feed is connected.", "bool", None, True),
        ("watch_notification_sounds", "Notification sounds", "Preference for future watchlist alerts.", "bool", None, True),
        ("watch_remember_status", "Remember previous statuses", "Preference saved; the current Watchlist continues its existing status-record behaviour.", "bool", None, True),
        ("watch_keep_history", "Keep status history", "Preference saved; the current Watchlist continues retaining its existing history.", "bool", None, True),
    ]),
    ("Generator", "Default preferences for the existing name generator.", [
        ("generator_quantity", "Default generation quantity", "Sets the starting quantity shown on the existing Name Generator page.", "number", (1, 500), True),
        ("generator_category", "Default generation category", "Sets the starting category shown on the existing Name Generator page.", "choice", ["4 Letter", "Clean", "Short", "Leetspeak"], True),
        ("generator_deduplicate", "Automatically remove duplicates", "Preference for generated name lists.", "bool", None, True),
        ("generator_ignore_case", "Ignore capitalisation for duplicates", "Compare names without regard to capitalisation.", "bool", None, True),
        ("generator_preserve_spelling", "Preserve original spelling", "Keep the first spelling encountered when finding duplicates.", "bool", None, True),
        ("generator_auto_copy", "Automatically copy generated names", "Optional generator preference; not connected to existing generator actions.", "bool", None, True),
    ]),
    ("Checker", "Preferences for the formatting checker. This is not Xbox availability checking.", [
        ("checker_auto_save", "Automatically save checked names", "Preference only; checker storage is not changed by this setting.", "bool", None, True),
        ("checker_remember_filters", "Remember previous filters", "Save a future filter preference.", "bool", None, True),
        ("checker_organise", "Automatically organise results", "Display preference.", "bool", None, True),
        ("checker_separate_valid", "Display valid and invalid names separately", "Display preference.", "bool", None, True),
        ("checker_availability", "Availability checking", "Unavailable: the checker validates formatting only.", "bool", None, False),
    ]),
    ("Import & Export", "Default folders and local file handling preferences.", [
        ("import_folder", "Default import folder", "Saved preference; the current importer does not yet read this setting.", "folder", None, True),
        ("export_folder", "Default export folder", "Saved preference; the current exporter does not yet read this setting.", "folder", None, True),
        ("import_deduplicate", "Remove duplicate imports", "Saved preference; the current importer does not yet read this setting.", "bool", None, True),
        ("import_ignore_blank", "Ignore blank lines", "Saved preference; the current importer does not yet read this setting.", "bool", None, True),
        ("export_format", "Preferred export format", "Saved preference; the current exporter does not yet read this setting.", "choice", ["TXT", "CSV", "JSON"], True),
        ("export_remember_location", "Remember previous export location", "Saved preference; the current exporter does not yet read this setting.", "bool", None, True),
    ]),
    ("Duplicate Finder", "Duplicate handling preferences; Duplicate Finder remains inside Settings.", [
        ("duplicate_enabled", "Enable Duplicate Finder", "Enable duplicate preference controls.", "bool", None, True),
        ("duplicate_auto", "Automatic duplicate detection", "Preference for duplicate detection.", "bool", None, True),
        ("duplicate_before_check", "Remove duplicates before checking", "Preference for future checker integration.", "bool", None, True),
        ("duplicate_ignore_case", "Ignore capitalisation", "Treat case-only variations as duplicates.", "bool", None, True),
        ("duplicate_preserve_spelling", "Preserve original spelling", "Keep the first observed spelling.", "bool", None, True),
        ("duplicate_history", "Duplicate activity history", "Preference for future history records.", "bool", None, True),
    ]),
    ("Proxy", "Proxy preferences. Direct connection remains the default; the Proxy Manager is unchanged.", [
        ("proxy_enabled", "Enable proxy usage", "Off by default. Proxy Manager tests saved proxies; other pages do not currently use them.", "bool", None, True),
        ("proxy_method", "Connection method", "Saved preference; no name-checking connection uses this choice.", "choice", ["Direct connection", "Use proxy"], True),
        ("proxy_protocol", "Default proxy protocol", "Preference for a future proxy consumer.", "choice", ["HTTP", "HTTPS", "SOCKS4", "SOCKS4a", "SOCKS5", "SOCKS5h"], True),
        ("proxy_auto_select", "Automatically select working proxy", "Preference; no consumer is connected here.", "bool", None, True),
        ("proxy_skip_failed", "Skip failed proxies", "Preference for proxy selection.", "bool", None, True),
        ("proxy_test_startup", "Test proxies on startup", "Off by default; this preference is not wired into startup.", "bool", None, True),
        ("proxy_timeout", "Connection timeout (seconds)", "Timeout preference for a future consumer.", "number", (1, 120), True),
        ("proxy_remember_selection", "Remember selected proxy", "Remember the preferred proxy selection.", "bool", None, True),
    ]),
    ("Notifications", "Choose notification preferences. Test Notification displays an in-app message.", [
        ("desktop_notifications", "Enable desktop notifications", "Windows toast delivery is not connected; this preference is saved.", "bool", None, True),
        ("in_app_notifications", "Enable in-app notifications", "Allow in-app notification messages.", "bool", None, True),
        ("notification_sounds", "Enable notification sounds", "Sound playback is not connected.", "bool", None, True),
        ("notify_watch_available", "Watched names become available", "Requires a genuine availability checker.", "bool", None, True),
        ("notify_proxy_finished", "Proxy testing finishes", "Preference for a future in-app proxy notice.", "bool", None, True),
        ("notify_updates", "Application updates", "Update notifications are not connected to a release feed.", "bool", None, True),
    ]),
    ("Storage & Backups", "Manage local application data and ZIP backups.", [
        ("auto_backups", "Enable automatic backups", "When enabled, create a local backup when its chosen interval has elapsed.", "bool", None, True),
        ("backup_frequency", "Backup frequency", "Automatic backup interval.", "choice", ["Daily", "Weekly", "Monthly"], True),
    ]),
    ("Updates", "Toolsy never updates itself automatically.", [
        ("enable_update_notifications", "Enable update notifications", "Stored preference; no update service is configured.", "bool", None, True),
    ]),
    ("About Toolsy", "Project status and developer information.", []),
]

SIZE_VALUES = {"Small": 9, "Default": 10, "Comfortable": 11, "Large": 12, "Extra Large": 14}
SIZE_LABELS = {v: k for k, v in SIZE_VALUES.items()}
SCALE_VALUES = {"90%": 90, "100%": 100, "110%": 110, "125%": 125, "150%": 150}


def load_settings():
    settings = deepcopy(DEFAULTS)
    try:
        stored = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(stored, dict):
            for key, default in DEFAULTS.items():
                value = stored.get(key, default)
                if isinstance(default, bool):
                    value = value if isinstance(value, bool) else default
                elif isinstance(default, int) and not isinstance(default, bool):
                    value = value if isinstance(value, int) else default
                elif isinstance(default, list):
                    value = [item for item in value if isinstance(item, dict)] if isinstance(value, list) else deepcopy(default)
                elif default is not None:
                    value = value if isinstance(value, str) else default
                settings[key] = value
    except (OSError, json.JSONDecodeError):
        pass
    if settings["theme"] not in ("Dark", "Light", "Executive", "Calm"):
        settings["theme"] = "Dark"
    if settings["density"] not in ("Comfortable", "Compact"):
        settings["density"] = "Comfortable"
    if settings["proxy_method"] not in ("Direct connection", "Use proxy"):
        settings["proxy_method"] = "Direct connection"
    settings["confirm_before_clearing"] = True
    return settings


def save_settings(settings):
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    temp = SETTINGS_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(SETTINGS_FILE)


def create_backup(destination=None):
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = Path(destination) if destination else BACKUP_PATH / f"toolsy_backup_{stamp}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        if DATA_PATH.exists():
            for file in DATA_PATH.glob("*.json"):
                archive.write(file, f"data/{file.name}")
    return target


def maybe_create_automatic_backup(settings):
    if not settings.get("auto_backups"):
        return None
    last = settings.get("last_backup", "")
    try:
        previous = datetime.fromisoformat(last)
    except (TypeError, ValueError):
        previous = None
    days = {"Daily": 1, "Weekly": 7, "Monthly": 30}.get(settings.get("backup_frequency"), 7)
    if previous and datetime.now() - previous < timedelta(days=days):
        return None
    path = create_backup()
    settings["last_backup"] = datetime.now().isoformat(timespec="seconds")
    save_settings(settings)
    return path


class SettingsPage(QWidget):
    settings_changed = Signal(dict)

    def __init__(self, settings, tray_available=True):
        super().__init__()
        self.settings = settings
        self.tray_available = tray_available
        self.controls = {}
        self.entries = {}
        self.category_pages = []
        self._build()
        self._populate()
        tray_control = self.controls.get("minimise_to_tray")
        if tray_control and not tray_available:
            tray_control.setEnabled(False)
            tray_control.setToolTip("System tray support is not available in this desktop session.")
        clear_control = self.controls.get("confirm_before_clearing")
        if clear_control:
            clear_control.setChecked(True)
            clear_control.setEnabled(False)

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 20, 28, 24)
        outer.setSpacing(10)
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Manage Toolsy preferences, appearance, and local data.")
        subtitle.setObjectName("pageSubtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search settings by name or description...")
        self.search.textChanged.connect(self._search)
        outer.addWidget(self.search)
        self.results = QListWidget()
        self.results.setMaximumHeight(145)
        self.results.hide()
        self.results.itemClicked.connect(self._open_result)
        outer.addWidget(self.results)

        body = QHBoxLayout()
        body.setSpacing(14)
        self.category_list = QListWidget()
        self.category_list.setObjectName("settingsCategories")
        self.category_list.setFixedWidth(205)
        self.stack = QStackedWidget()
        for name, description, rows in CATEGORIES:
            self.category_list.addItem(name)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(4, 4, 8, 12)
            page_layout.setSpacing(10)
            heading = QLabel(name)
            heading.setObjectName("settingsHeading")
            desc = QLabel(description)
            desc.setObjectName("mutedText")
            desc.setWordWrap(True)
            page_layout.addWidget(heading)
            page_layout.addWidget(desc)
            if name == "Storage & Backups":
                self._storage_info(page_layout)
            for row in rows:
                page_layout.addWidget(self._setting_row(row))
            if name == "General":
                reset = QPushButton("Reset Settings to Defaults")
                reset.clicked.connect(self.reset_settings)
                page_layout.addWidget(reset)
            elif name == "Storage & Backups":
                self._storage_actions(page_layout)
            elif name == "Notifications":
                test = QPushButton("Test Notification")
                test.clicked.connect(self.test_notification)
                page_layout.addWidget(test)
                history = QPushButton("View Notification History")
                history.clicked.connect(self.view_notification_history)
                page_layout.addWidget(history)
            elif name == "Updates":
                version = QLabel(f"Current version: {VERSION}\nAutomatic updates are disabled. No release feed or Discord invite is configured.")
                version.setObjectName("mutedText")
                version.setWordWrap(True)
                page_layout.addWidget(version)
                check = QPushButton("Check for Updates")
                check.clicked.connect(lambda: QMessageBox.information(self, "Updates", "No update service is configured. Toolsy will not update itself."))
                page_layout.addWidget(check)
                discord = QPushButton("Open Toolsy Discord")
                discord.setEnabled(False)
                discord.setToolTip("No Discord invite URL is configured in the project.")
                page_layout.addWidget(discord)
            elif name == "About Toolsy":
                about = QFrame()
                about.setObjectName("aboutCard")
                about_layout = QVBoxLayout(about)
                about_layout.setContentsMargins(22, 20, 22, 20)
                about_layout.setSpacing(9)
                app_name = QLabel("Toolsy")
                app_name.setObjectName("aboutTitle")
                developer = QLabel("Developer: C0d3lne")
                developer.setObjectName("settingsLabel")
                status = QLabel("In development")
                status.setObjectName("aboutStatus")
                details = QLabel("Toolsy is still a work in progress. No API is currently connected, so name checks do not verify Xbox availability. Expect bugs while development continues.")
                details.setObjectName("mutedText")
                details.setWordWrap(True)
                for item in (app_name, developer, status, details):
                    about_layout.addWidget(item)
                page_layout.addWidget(about)
            scroll.setWidget(page)
            self.category_pages.append((page, scroll))
            self.stack.addWidget(scroll)
        self.category_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.category_list.setCurrentRow(0)
        body.addWidget(self.category_list)
        body.addWidget(self.stack, 1)
        outer.addLayout(body, 1)

    def _setting_row(self, row):
        key, title, description, kind, choices, enabled = row
        card = QFrame()
        card.setObjectName("settingsCard")
        box = QHBoxLayout(card)
        box.setContentsMargins(14, 10, 14, 10)
        box.setSpacing(12)
        words = QVBoxLayout()
        label = QLabel(title)
        label.setObjectName("settingsLabel")
        detail = QLabel(description)
        detail.setObjectName("mutedText")
        detail.setWordWrap(True)
        words.addWidget(label)
        words.addWidget(detail)
        box.addLayout(words, 1)
        if kind == "bool":
            control = QCheckBox()
            control.setChecked(bool(self.settings.get(key)))
            control.stateChanged.connect(lambda state, k=key: self._set(k, bool(state)))
        elif kind == "number":
            control = QSpinBox()
            control.setRange(*choices)
            control.valueChanged.connect(lambda value, k=key: self._set(k, value))
        elif kind == "folder":
            control = QLineEdit(str(self.settings.get(key, "")))
            control.setMinimumWidth(180)
            control.editingFinished.connect(lambda k=key, c=control: self._set(k, c.text()))
            browse = QPushButton("Browse")
            browse.clicked.connect(lambda _=False, k=key, c=control: self._browse_folder(k, c))
            box.addWidget(control)
            box.addWidget(browse)
        else:
            control = QComboBox()
            if key == "font":
                families = set(QFontDatabase.families())
                preferred = ("Segoe UI Variable", "Segoe UI", "Aptos", "Inter", "Roboto", "Bahnschrift", "Calibri", "Candara", "Cascadia Code", "Consolas", "Arial", "Tahoma", "Trebuchet MS", "Verdana", "Georgia", "Times New Roman", "Century Gothic", "Courier New", "Impact")
                values = [name for name in preferred if name in families]
                choices = values or ["Segoe UI"]
            control.addItems(choices)
            value = self.settings.get(key)
            if key == "font_size":
                value = SIZE_LABELS.get(value, "Default")
            elif key == "interface_scale":
                value = f"{value}%"
            index = control.findText(str(value))
            control.setCurrentIndex(index if index >= 0 else 0)
            control.currentTextChanged.connect(lambda value, k=key: self._choice_changed(k, value))
        control.setEnabled(enabled)
        control.setToolTip(description)
        if kind != "folder":
            box.addWidget(control)
        self.controls[key] = control
        self.entries[key] = (title, description, card)
        return card

    def _storage_info(self, layout):
        size = sum(f.stat().st_size for f in DATA_PATH.glob("*") if f.is_file()) if DATA_PATH.exists() else 0
        info = QLabel(f"Storage location: {DATA_PATH}\nCurrent data usage: {size / 1024:.1f} KB")
        info.setObjectName("mutedText")
        info.setWordWrap(True)
        layout.addWidget(info)
        self.storage_info = info

    def _storage_actions(self, layout):
        row = QHBoxLayout()
        view = QPushButton("Open Storage Folder")
        view.clicked.connect(self.open_storage)
        backup = QPushButton("Create Backup")
        backup.clicked.connect(self.backup_now)
        restore = QPushButton("Restore from Backup")
        restore.clicked.connect(self.restore_backup)
        export = QPushButton("Export Application Data")
        export.clicked.connect(self.export_data)
        clear = QPushButton("Clear Selected Data")
        clear.clicked.connect(self.clear_data)
        for button in (view, backup, restore, export, clear):
            row.addWidget(button)
        layout.addLayout(row)

    def _populate(self):
        for key, control in self.controls.items():
            if key not in self.settings:
                continue
            if isinstance(control, QCheckBox):
                control.blockSignals(True); control.setChecked(bool(self.settings[key])); control.blockSignals(False)
            elif isinstance(control, QSpinBox):
                control.blockSignals(True); control.setValue(int(self.settings[key])); control.blockSignals(False)
            elif isinstance(control, QComboBox):
                value = self.settings[key]
                if key == "font_size": value = SIZE_LABELS.get(value, "Default")
                if key == "interface_scale": value = f"{value}%"
                idx = control.findText(str(value))
                if idx >= 0: control.setCurrentIndex(idx)
            elif isinstance(control, QLineEdit):
                control.setText(str(self.settings[key]))

    def _set(self, key, value):
        self.settings[key] = value
        if key == "compact_mode":
            self.settings["density"] = "Compact" if value else "Comfortable"
            self._populate()
        elif key == "density":
            self.settings["compact_mode"] = value == "Compact"
            self._populate()
        self._persist()

    def _choice_changed(self, key, value):
        if key == "font_size": value = SIZE_VALUES[value]
        elif key == "interface_scale": value = SCALE_VALUES[value]
        self._set(key, value)

    def _persist(self):
        save_settings(self.settings)
        self.settings_changed.emit(self.settings)

    def _browse_folder(self, key, control):
        folder = QFileDialog.getExistingDirectory(self, "Choose Folder", control.text())
        if folder:
            control.setText(folder)
            self._set(key, folder)

    def _search(self, text):
        self.results.clear()
        query = text.strip().casefold()
        if not query:
            self.results.hide()
            return
        found = 0
        for ci, (name, _desc, rows) in enumerate(CATEGORIES):
            for row in rows:
                key, title, description = row[:3]
                if query in title.casefold() or query in description.casefold() or query in name.casefold():
                    item = QListWidgetItem(f"{title}  ·  {name}\n{description}")
                    item.setData(Qt.ItemDataRole.UserRole, (ci, key))
                    self.results.addItem(item)
                    found += 1
        if not found:
            self.results.addItem("No matching settings")
        self.results.setVisible(True)

    def _open_result(self, item):
        target = item.data(Qt.ItemDataRole.UserRole)
        if not target:
            return
        ci, key = target
        self.category_list.setCurrentRow(ci)
        page, _scroll = self.category_pages[ci]
        entry = self.entries.get(key)
        if entry:
            entry[2].setStyleSheet("border: 2px solid palette(highlight);")
            entry[2].setFocus()
            self.category_pages[ci][1].ensureWidgetVisible(entry[2])
        self.results.hide()

    def reset_settings(self):
        answer = QMessageBox.question(self, "Reset Settings", "Restore all preferences to defaults? Your gamertags, watchlist, proxies, backups, and other saved data will remain untouched.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.settings.clear()
        self.settings.update(deepcopy(DEFAULTS))
        self._populate()
        self._persist()

    def test_notification(self):
        self.settings.setdefault("notification_history", []).append({"date": datetime.now().isoformat(timespec="seconds"), "message": "Test notification"})
        self.settings["notification_history"] = self.settings["notification_history"][-100:]
        self._persist()
        if self.settings.get("in_app_notifications"):
            QMessageBox.information(self, "Test Notification", "Toolsy in-app notifications are working.")
        else:
            QMessageBox.information(self, "Notifications Disabled", "In-app notifications are disabled in Settings.")

    def view_notification_history(self):
        history = self.settings.get("notification_history", [])
        message = "\n".join(f"{item.get('date','')} — {item.get('message','')}" for item in reversed(history[-30:])) or "No notification history."
        QMessageBox.information(self, "Notification History", message)

    def open_storage(self):
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(DATA_PATH))
        except (AttributeError, OSError) as error:
            QMessageBox.warning(self, "Storage Folder", f"Storage location:\n{DATA_PATH}\n\nCould not open the folder: {error}")

    def backup_now(self):
        path = create_backup()
        self.settings["last_backup"] = datetime.now().isoformat(timespec="seconds")
        self._persist()
        self.storage_info.setText(f"Storage location: {DATA_PATH}\nBackup created: {path}")
        QMessageBox.information(self, "Backup Created", f"Local backup saved to:\n{path}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Application Data", str(BACKUP_PATH / "toolsy_export.zip"), "ZIP Files (*.zip)")
        if path:
            result = create_backup(path)
            QMessageBox.information(self, "Export Complete", f"Application data exported to:\n{result}")

    def restore_backup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Restore Application Backup", str(BACKUP_PATH), "ZIP Files (*.zip)")
        if not path:
            return
        try:
            with zipfile.ZipFile(path) as archive:
                members = [m for m in archive.namelist() if m.startswith("data/") and Path(m).name.endswith(".json") and Path(m).name == m.split("/")[-1]]
                if not members:
                    raise ValueError("The ZIP contains no valid data JSON files.")
                for member in members:
                    json.loads(archive.read(member).decode("utf-8"))
        except (OSError, zipfile.BadZipFile, UnicodeError, json.JSONDecodeError, ValueError) as error:
            QMessageBox.critical(self, "Restore Failed", f"Backup could not be read safely:\n{error}")
            return
        if QMessageBox.question(self, "Restore Backup", "Restore the JSON files in this backup? Existing files with matching names will be replaced.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path) as archive:
            for member in members:
                (DATA_PATH / Path(member).name).write_bytes(archive.read(member))
        QMessageBox.information(self, "Restore Complete", "Backup data has been restored. Restart Toolsy to reload all saved data.")

    def clear_data(self):
        files = sorted(f.name for f in DATA_PATH.glob("*.json") if f.is_file()) if DATA_PATH.exists() else []
        if not files:
            QMessageBox.information(self, "Clear Data", "There are no JSON data files to clear.")
            return
        choice, ok = QInputDialog.getItem(self, "Clear Selected Data", "Choose one JSON data file to clear:", files, 0, False)
        if not ok:
            return
        answer = QMessageBox.question(self, "Confirm Data Removal", f"Permanently clear {choice}? This cannot be undone unless you have a backup.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        (DATA_PATH / choice).write_text("[]\n", encoding="utf-8")
        if choice == "settings.json":
            (DATA_PATH / choice).write_text("{}\n", encoding="utf-8")
        QMessageBox.information(self, "Data Cleared", f"Cleared {choice}.")
