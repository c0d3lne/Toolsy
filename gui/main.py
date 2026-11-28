import sys
import json
from pathlib import Path

from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QFont, QGuiApplication, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QSizePolicy,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
)

PROJECT_PATH = Path(__file__).resolve().parent.parent
if str(PROJECT_PATH) not in sys.path:
    sys.path.insert(0, str(PROJECT_PATH))

from import_page import ImportPage
from checker_page import NameCheckerPage
from generator_page import NameGeneratorPage
from claim_page import ClaimNamesPage
from proxy_page import ProxyManagerPage
from watchlist_page import WatchlistPage
from settings_page import (
    SettingsPage, load_settings, save_settings, maybe_create_automatic_backup,
)
from theme_manager import apply_theme


CLAIM_HISTORY_FILE = PROJECT_PATH / "data" / "claim_history.json"


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(22)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Welcome to Toolsy. Your gamertag workspace."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # STATISTICS

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.total_value = self.create_stat(
            stats_layout, "TOTAL NAMES"
        )

        self.valid_value = self.create_stat(
            stats_layout, "VALID NAMES"
        )

        self.invalid_value = self.create_stat(
            stats_layout, "INVALID NAMES"
        )

        layout.addLayout(stats_layout)

        # RECENT ACTIVITY

        activity_panel = QFrame()
        activity_panel.setObjectName("panel")

        activity_layout = QVBoxLayout(activity_panel)
        activity_layout.setContentsMargins(22, 20, 22, 20)

        activity_title = QLabel("RECENT ACTIVITY")
        activity_title.setObjectName("sectionTitle")

        self.activity_text = QLabel(
            "No recent activity.\n\n"
            "Import a gamertag list to get started."
        )
        self.activity_text.setObjectName("mutedText")

        self.activity_text.setWordWrap(True)

        activity_layout.addWidget(activity_title)
        activity_layout.addWidget(self.activity_text)

        layout.addWidget(activity_panel)

        # CLAIM HISTORY

        claim_panel = QFrame()
        claim_panel.setObjectName("panel")

        claim_layout = QVBoxLayout(claim_panel)
        claim_layout.setContentsMargins(22, 20, 22, 20)
        claim_layout.setSpacing(12)

        claim_title = QLabel("RECENT CLAIM ACTIVITY")
        claim_title.setObjectName("sectionTitle")

        self.claim_history_label = QLabel(
            "No claim attempts recorded."
        )
        self.claim_history_label.setObjectName("mutedText")
        self.claim_history_label.setWordWrap(True)

        self.clear_claim_button = QPushButton(
            "Clear Claim History"
        )

        self.clear_claim_button.clicked.connect(
            self.clear_claim_history
        )

        claim_layout.addWidget(claim_title)
        claim_layout.addWidget(self.claim_history_label)
        claim_layout.addWidget(self.clear_claim_button)

        layout.addWidget(claim_panel)

        # SYSTEM INFORMATION

        system_panel = QFrame()
        system_panel.setObjectName("panel")

        system_layout = QVBoxLayout(system_panel)
        system_layout.setContentsMargins(22, 20, 22, 20)

        system_title = QLabel("SYSTEM INFORMATION")
        system_title.setObjectName("sectionTitle")

        system_text = QLabel(
            "APPLICATION: TOOLSY\n"
            "PLATFORM: WINDOWS\n"
            "MODE: LOCAL DESKTOP APPLICATION\n"
            "AVAILABILITY: NOT CONNECTED"
        )

        system_text.setObjectName("mutedText")

        system_layout.addWidget(system_title)
        system_layout.addWidget(system_text)

        layout.addWidget(system_panel)
        layout.addStretch()

        self.refresh_claim_history()

    def create_stat(self, parent_layout, heading):

        card = QFrame()
        card.setObjectName("statCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)

        heading_label = QLabel(heading)
        heading_label.setObjectName("statHeading")

        value_label = QLabel("0")
        value_label.setObjectName("statValue")

        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)

        parent_layout.addWidget(card)

        return value_label

    def refresh_claim_history(self):

        if not CLAIM_HISTORY_FILE.exists():

            self.claim_history_label.setText(
                "No claim attempts recorded."
            )

            return

        try:

            with open(
                CLAIM_HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                history = json.load(file)

            if not isinstance(history, list):
                history = []

        except (OSError, json.JSONDecodeError):

            history = []

        if not history:

            self.claim_history_label.setText(
                "No claim attempts recorded."
            )

            return

        lines = []

        for entry in history[:5]:

            if not isinstance(entry, dict):
                continue

            lines.append(
                f"{entry.get('gamertag', 'Unknown')}  —  "
                f"{entry.get('date', 'Unknown date')}"
            )

        self.claim_history_label.setText(
            "\n".join(lines) if lines
            else "No claim attempts recorded."
        )

    def clear_claim_history(self):

        if not CLAIM_HISTORY_FILE.exists():
            return

        confirm = QMessageBox.question(
            self,
            "Clear Claim History",
            "Permanently clear all claim history?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        CLAIM_HISTORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            CLAIM_HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file, indent=4)

        self.refresh_claim_history()


class PlaceholderPage(QWidget):

    def __init__(self, title, description):

        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(15)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")

        subtitle = QLabel(description)
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(25, 25, 25, 25)

        message = QLabel(
            "This section is currently under development."
        )
        message.setObjectName("mutedText")

        panel_layout.addWidget(message)

        layout.addWidget(panel)
        layout.addStretch()


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.settings = load_settings()
        save_settings(self.settings)

        self.setWindowTitle("Toolsy")
        self.setMinimumSize(1000, 650)
        if self.settings.get("remember_window_size", True):
            self.resize(
                max(1000, int(self.settings.get("window_width", 1400))),
                max(650, int(self.settings.get("window_height", 850))),
            )
        else:
            self.resize(1400, 850)

        self.import_page = None
        self.checker_page = None
        self.generator_page = None
        self.claim_page = None
        self.dashboard_page = None
        self.watchlist_page = None
        self.settings_page = None
        self.tray_icon = None
        self._last_startup_setting = self.settings.get("launch_on_startup", False)
        self._stored_window_size = (
            self.settings.get("window_width", 1400),
            self.settings.get("window_height", 850),
        )
        self._stored_window_position = (
            self.settings.get("window_x"), self.settings.get("window_y")
        )

        self.build_interface()
        self._restore_window_geometry()
        self._setup_tray()
        self.apply_current_settings()
        maybe_create_automatic_backup(self.settings)
        if self.settings.get("remember_last_page"):
            last_page = int(self.settings.get("last_page", 0))
            if 0 <= last_page < self.pages.count():
                self.change_page(last_page)

    def build_interface(self):

        central = QWidget()
        central.setObjectName("appRoot")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(225)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 25, 16, 20)
        sidebar_layout.setSpacing(8)

        logo = QLabel("Toolsy")
        logo.setObjectName("logo")

        logo_subtitle = QLabel("GAMERTAG WORKSPACE")
        logo_subtitle.setObjectName("logoSubtitle")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(logo_subtitle)
        sidebar_layout.addSpacing(30)

        navigation = [
            ("◈", "Dashboard"),
            ("✦", "Name Generator"),
            ("⌕", "Name Checker"),
            ("➜", "Claim Names"),
            ("◎", "Proxy Manager"),
            ("☆", "Watchlist"),
            ("⇧", "Import"),
            ("⚙", "Settings"),
        ]

        descriptions = {
            "Proxy Manager": "Manage your proxy connections.",
            "Watchlist": "Monitor selected gamertags.",
            "Settings": "Application settings and preferences.",
        }

        content_area = QVBoxLayout()
        content_area.setContentsMargins(0, 0, 0, 0)
        content_area.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(60)

        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(25, 0, 25, 0)

        topbar_title = QLabel("Toolsy")
        topbar_title.setObjectName("topbarTitle")

        status = QLabel("LOCAL APPLICATION")
        status.setObjectName("statusText")

        topbar_layout.addWidget(topbar_title)
        topbar_layout.addStretch()
        topbar_layout.addWidget(status)

        content_area.addWidget(topbar)

        self.pages = QStackedWidget()
        self.pages.setObjectName("appPages")
        content_area.addWidget(self.pages)

        self.navigation_buttons = []

        for icon, name in navigation:

            button = QPushButton(f"{icon}    {name}")
            button.setObjectName("navButton")
            button.setProperty("active", False)

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            sidebar_layout.addWidget(button)

            page_index = self.pages.count()

            if name == "Dashboard":

                self.dashboard_page = DashboardPage()
                page = self.dashboard_page

            elif name == "Name Generator":

                self.generator_page = NameGeneratorPage()
                self._apply_generator_preferences()
                page = self.generator_page

            elif name == "Name Checker":

                self.checker_page = NameCheckerPage()
                page = self.checker_page

            elif name == "Import":

                self.import_page = ImportPage()
                page = self.import_page

            elif name == "Claim Names":

                self.claim_page = ClaimNamesPage()
                page = self.claim_page

            elif name == "Proxy Manager":

                page = ProxyManagerPage()

            elif name == "Watchlist":

                self.watchlist_page = WatchlistPage()
                page = self.watchlist_page

            elif name == "Settings":

                self.settings_page = SettingsPage(
                    self.settings,
                    tray_available=QSystemTrayIcon.isSystemTrayAvailable(),
                )
                self.settings_page.settings_changed.connect(
                    self.settings_updated
                )
                page = self.settings_page

            else:

                page = PlaceholderPage(
                    name,
                    descriptions.get(
                        name,
                        "This section is currently under development."
                    )
                )

            self.pages.addWidget(page)

            button.clicked.connect(
                lambda checked=False, index=page_index:
                self.change_page(index)
            )

            self.navigation_buttons.append(button)

        sidebar_layout.addStretch()

        version_label = QLabel("TOOLSY  |  VERSION 1.0")
        version_label.setObjectName("statusText")

        sidebar_layout.addWidget(version_label)

        if self.import_page and self.checker_page:

            self.import_page.names_imported.connect(
                self.checker_page.set_gamertags
            )
            self.import_page.names_ready_for_checker.connect(
                self.open_checker_with_names
            )
        if self.generator_page and self.checker_page:
            self.generator_page.names_ready_for_checker.connect(
                self.open_checker_with_names
            )

        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_area)

        self.change_page(0)

    def open_checker_with_names(self, names):
        if self.checker_page:
            self.checker_page.set_gamertags(names)
            checker_index = self.pages.indexOf(self.checker_page)
            if checker_index >= 0:
                self.change_page(checker_index)

    def change_page(self, index):

        self.pages.setCurrentIndex(index)

        if self.settings.get("remember_last_page"):
            self.settings["last_page"] = index
            save_settings(self.settings)

        if self.pages.widget(index) is self.watchlist_page:
            self.watchlist_page.show_unseen_alerts()

        if index == 0 and self.dashboard_page:
            self.dashboard_page.refresh_claim_history()

        for button_index, button in enumerate(
            self.navigation_buttons
        ):

            button.setProperty(
                "active",
                button_index == index
            )

            button.style().unpolish(button)
            button.style().polish(button)

    def _restore_window_geometry(self):
        screens = QGuiApplication.screens()
        if not screens:
            return
        width = self.width()
        height = self.height()
        if self.settings.get("remember_window_size", True):
            width = max(1000, int(self.settings.get("window_width", width)))
            height = max(650, int(self.settings.get("window_height", height)))
            self.resize(width, height)
        if not self.settings.get("remember_window_position", True):
            return
        x, y = self.settings.get("window_x"), self.settings.get("window_y")
        if not isinstance(x, int) or not isinstance(y, int):
            return
        saved = QRect(x, y, width, height)
        visible = any(
            (saved & screen.availableGeometry()).width() >= 100
            and (saved & screen.availableGeometry()).height() >= 80
            for screen in screens
        )
        if visible:
            self.move(x, y)
            return
        screen = QGuiApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            self.move(area.center().x() - width // 2, area.center().y() - height // 2)

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(
            self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon), self
        )
        menu = QMenu(self)
        open_action = QAction("Open Toolsy", self)
        open_action.triggered.connect(self._restore_from_tray)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._tray_activated)

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restore_from_tray()

    def _restore_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        if self.tray_icon:
            self.tray_icon.hide()

    def changeEvent(self, event):
        super().changeEvent(event)
        if (event.type() == QEvent.Type.WindowStateChange
                and self.isMinimized()
                and self.settings.get("minimise_to_tray")
                and self.tray_icon):
            self.tray_icon.show()
            self.hide()

    def settings_updated(self, settings):
        old_startup = self._last_startup_setting
        previous_size = self._stored_window_size
        previous_position = self._stored_window_position
        self.settings = settings
        self.apply_current_settings()
        self._apply_generator_preferences()
        current_size = (
            settings.get("window_width", 1400),
            settings.get("window_height", 850),
        )
        current_position = (settings.get("window_x"), settings.get("window_y"))
        if settings.get("remember_window_size", True) and current_size != previous_size:
            self.resize(max(1000, int(current_size[0])), max(650, int(current_size[1])))
        if settings.get("remember_window_position", True) and current_position != previous_position:
            if not all(isinstance(value, int) for value in current_position):
                screen = QGuiApplication.primaryScreen()
                if screen:
                    area = screen.availableGeometry()
                    self.move(area.center().x() - self.width() // 2, area.center().y() - self.height() // 2)
            else:
                self._restore_window_geometry()
        self._stored_window_size = current_size
        self._stored_window_position = current_position
        if settings.get("launch_on_startup") != old_startup:
            try:
                self._set_startup_registration(settings["launch_on_startup"])
                self._last_startup_setting = settings["launch_on_startup"]
            except (OSError, ImportError) as error:
                self.settings["launch_on_startup"] = old_startup
                save_settings(self.settings)
                if self.settings_page:
                    self.settings_page._populate()
                QMessageBox.warning(self, "Startup Setting", f"Could not update Windows startup registration:\n{error}")

    def _apply_generator_preferences(self):
        if not self.generator_page:
            return
        category = self.settings.get("generator_category", "4 Letter")
        category_index = self.generator_page.category.findText(category)
        if category_index >= 0:
            self.generator_page.category.setCurrentIndex(category_index)
        quantity = max(1, min(500, int(self.settings.get("generator_quantity", 25))))
        self.generator_page.amount.setValue(quantity)

    def _set_startup_registration(self, enabled):
        if sys.platform != "win32":
            raise OSError("Windows startup registration is only available on Windows.")
        import winreg
        import subprocess

        run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                pythonw = Path(sys.executable).with_name("pythonw.exe")
                executable = str(pythonw if pythonw.exists() else Path(sys.executable))
                command = [executable, str(Path(__file__).resolve())]
                if self.settings.get("minimise_on_startup"):
                    command.append("--minimised")
                winreg.SetValueEx(key, "Toolsy", 0, winreg.REG_SZ, subprocess.list2cmdline(command))
            else:
                try:
                    winreg.DeleteValue(key, "Toolsy")
                except FileNotFoundError:
                    pass

    def apply_current_settings(self):
        app = QApplication.instance()
        if app:
            apply_theme(app, self.settings, self)
            base = int(self.settings.get("font_size", 10))
            scale = int(self.settings.get("interface_scale", 100))
            font_size = max(8, min(20, round(base * scale / 100)))
            font = self.settings.get("font", "Segoe UI")
            app.setFont(QFont(font, font_size))
        compact = self.settings.get("compact_mode") or self.settings.get("density") == "Compact"
        for page in getattr(self, "pages", []).findChildren(QWidget) if hasattr(self, "pages") else []:
            layout = page.layout()
            if not layout:
                continue
            original = getattr(layout, "_null_original_margins", None)
            spacing = getattr(layout, "_null_original_spacing", None)
            if original is None:
                margins = layout.contentsMargins()
                original = (margins.left(), margins.top(), margins.right(), margins.bottom())
                layout._null_original_margins = original
                layout._null_original_spacing = layout.spacing()
                spacing = layout.spacing()
            factor = 0.55 if compact else 1.0
            layout.setContentsMargins(*(max(2, round(x * factor)) for x in original))
            if spacing >= 0:
                layout.setSpacing(max(3, round(spacing * factor)))

    def closeEvent(self, event):
        if self.settings.get("confirm_before_closing"):
            answer = QMessageBox.question(
                self, "Close Toolsy", "Are you sure you want to close Toolsy?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        if self.settings.get("remember_window_size", True):
            self.settings["window_width"] = self.width()
            self.settings["window_height"] = self.height()
        if self.settings.get("remember_window_position", True):
            self.settings["window_x"] = self.x()
            self.settings["window_y"] = self.y()
        save_settings(self.settings)
        if self.tray_icon:
            self.tray_icon.hide()
        event.accept()


def main():

    minimised = "--minimised" in sys.argv
    if minimised:
        sys.argv.remove("--minimised")
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()
    if minimised or window.settings.get("minimise_on_startup"):
        window.showMinimized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
