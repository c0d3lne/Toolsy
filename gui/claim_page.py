import json
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)


PROJECT_PATH = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_PATH / "data"
CLAIM_HISTORY_FILE = DATA_FOLDER / "claim_history.json"

XBOX_CLAIM_URL = "https://social.xbox.com/changegamertag"


class ClaimNamesPage(QWidget):

    def __init__(self):
        super().__init__()

        self.results = []
        self.claim_history = []

        self.load_history()
        self.build_ui()
        self.refresh_page()

    def build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(20)

        heading = QLabel("Claim Names")
        heading.setObjectName("pageTitle")

        subtitle = QLabel(
            "Manage available gamertags and open the official Xbox claiming process."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)

        # STATISTICS

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.available_stat = self.create_stat(
            "AVAILABLE", "0"
        )

        self.valid_stat = self.create_stat(
            "VALID FORMATS", "0"
        )

        self.attempts_stat = self.create_stat(
            "CLAIM ATTEMPTS", "0"
        )

        stats_layout.addWidget(self.available_stat)
        stats_layout.addWidget(self.valid_stat)
        stats_layout.addWidget(self.attempts_stat)

        layout.addLayout(stats_layout)

        # AVAILABLE NAMES

        panel = QFrame()
        panel.setObjectName("panel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 22, 22, 22)
        panel_layout.setSpacing(15)

        title = QLabel("AVAILABLE GAMERTAGS")
        title.setObjectName("sectionTitle")

        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter:")
        filter_label.setObjectName("mutedText")

        self.filter_combo = QComboBox()

        self.filter_combo.addItems([
            "All Available Names",
            "4 Characters",
            "5–7 Characters",
            "8+ Characters",
        ])

        self.filter_combo.currentIndexChanged.connect(
            self.refresh_table
        )

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "GAMERTAG",
            "LENGTH",
            "DATE AVAILABLE",
            "ACTION",
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        for column in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents
            )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.verticalHeader().setVisible(False)

        panel_layout.addWidget(title)
        panel_layout.addLayout(filter_layout)
        panel_layout.addWidget(self.table)

        layout.addWidget(panel)

        # CLAIM HISTORY

        history_panel = QFrame()
        history_panel.setObjectName("panel")

        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(22, 22, 22, 22)
        history_layout.setSpacing(12)

        history_title = QLabel("RECENT CLAIM ACTIVITY")
        history_title.setObjectName("sectionTitle")

        self.history_label = QLabel(
            "No claim attempts recorded."
        )
        self.history_label.setObjectName("mutedText")
        self.history_label.setWordWrap(True)

        self.clear_history_button = QPushButton(
            "Clear Claim History"
        )

        self.clear_history_button.clicked.connect(
            self.clear_history
        )

        history_layout.addWidget(history_title)
        history_layout.addWidget(self.history_label)
        history_layout.addWidget(self.clear_history_button)

        layout.addWidget(history_panel)
        layout.addStretch()

    # STATISTICS

    def create_stat(self, title, value):

        frame = QFrame()
        frame.setObjectName("statCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setObjectName("statHeading")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame.value_label = value_label

        return frame

    # RESULTS CONNECTION

    def set_results(self, results):

        self.results = list(results)

        self.refresh_page()

    def get_available_names(self):

        available = []

        for result in self.results:

            availability = str(
                result.get("availability_status", "")
            ).upper()

            if availability == "AVAILABLE":
                available.append(result)

        return available

    # REFRESH PAGE

    def refresh_page(self):

        available = self.get_available_names()

        valid = sum(
            1 for result in self.results
            if str(result.get("status", "")).upper() == "VALID"
        )

        self.available_stat.value_label.setText(
            str(len(available))
        )

        self.valid_stat.value_label.setText(
            str(valid)
        )

        self.attempts_stat.value_label.setText(
            str(len(self.claim_history))
        )

        self.refresh_table()
        self.refresh_history()

    # TABLE

    def refresh_table(self):

        available = self.get_available_names()

        selected_filter = self.filter_combo.currentIndex()

        def matches_filter(result):

            name = result.get("gamertag", "")
            length = len(name)

            if selected_filter == 1:
                return length == 4

            if selected_filter == 2:
                return 5 <= length <= 7

            if selected_filter == 3:
                return length >= 8

            return True

        matching = [
            result for result in available
            if matches_filter(result)
        ]

        other = [
            result for result in available
            if not matches_filter(result)
        ]

        self.table.clearContents()
        self.table.setRowCount(0)

        for result in matching:
            self.add_name_row(result)

        if other:

            self.add_section("OTHER AVAILABLE NAMES")

            for result in other:
                self.add_name_row(result)

        if not matching and not other:

            self.table.setRowCount(1)

            item = QTableWidgetItem(
                "No confirmed available gamertags yet."
            )

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 4)

    def add_section(self, title):

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setSpan(row, 0, 1, 4)

        item = QTableWidgetItem(title)

        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
        )

        self.table.setItem(row, 0, item)

    def add_name_row(self, result):

        row = self.table.rowCount()
        self.table.insertRow(row)

        name = result.get("gamertag", "")

        date = result.get(
            "available_since",
            "Recently checked"
        )

        self.table.setItem(
            row, 0, QTableWidgetItem(name)
        )

        self.table.setItem(
            row, 1, QTableWidgetItem(str(len(name)))
        )

        self.table.setItem(
            row, 2, QTableWidgetItem(str(date))
        )

        claim_button = QPushButton("CLAIM")

        claim_button.clicked.connect(
            lambda checked=False, gamertag=name:
            self.claim_name(gamertag)
        )

        self.table.setCellWidget(
            row, 3, claim_button
        )

    # CLAIM

    def claim_name(self, gamertag):

        confirm = QMessageBox.question(
            self,
            "Claim Gamertag",
            f"Open the official Xbox claiming page for:\n\n"
            f"{gamertag}?\n\n"
            f"You will complete the process yourself.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        QDesktopServices.openUrl(
            QUrl(XBOX_CLAIM_URL)
        )

        self.claim_history.insert(0, {
            "gamertag": gamertag,
            "date": datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        })

        self.save_history()
        self.refresh_page()

    # HISTORY

    def load_history(self):

        DATA_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        if CLAIM_HISTORY_FILE.exists():

            try:

                with open(
                    CLAIM_HISTORY_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                    if isinstance(data, list):
                        self.claim_history = [
                            entry for entry in data
                            if isinstance(entry, dict)
                        ]

            except (OSError, json.JSONDecodeError):
                self.claim_history = []

    def save_history(self):

        DATA_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            CLAIM_HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.claim_history,
                file,
                indent=4
            )

    def refresh_history(self):

        if not self.claim_history:

            self.history_label.setText(
                "No claim attempts recorded."
            )

            return

        recent = self.claim_history[:5]

        lines = []

        for entry in recent:

            lines.append(
                f"{entry.get('gamertag', 'Unknown')}  —  "
                f"{entry.get('date', 'Unknown date')}"
            )

        self.history_label.setText(
            "\n".join(lines)
        )

    def clear_history(self):

        if not self.claim_history:
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

        self.claim_history.clear()

        self.save_history()
        self.refresh_page()