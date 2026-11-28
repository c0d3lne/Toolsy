from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)

from toolsy_core.validator import validate_gamertags, ValidationStatus


class NameCheckerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.gamertags = []
        self.results = []
        self.results_updated_callback = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(18)

        title = QLabel("Name Checker")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Check gamertag formatting and identify invalid names.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.total_label = QLabel("TOTAL NAMES: 0")
        self.valid_label = QLabel("VALID: 0")
        self.invalid_label = QLabel("INVALID: 0")
        for label in (self.total_label, self.valid_label, self.invalid_label):
            label.setObjectName("sectionTitle")
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 18, 18, 18)
            card_layout.addWidget(label)
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search gamertags...")
        self.search_input.textChanged.connect(self.filter_results)
        self.check_button = QPushButton("CHECK ALL NAMES")
        self.check_button.clicked.connect(self.check_names)
        controls.addWidget(self.search_input)
        controls.addWidget(self.check_button)
        layout.addLayout(controls)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["GAMERTAG", "STATUS", "REASON / NOTES"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.status_label = QLabel("Import names before checking them.")
        self.status_label.setObjectName("mutedText")
        layout.addWidget(self.status_label)

    def set_gamertags(self, gamertags):
        self.gamertags = list(gamertags)
        self.results = []
        self.table.setRowCount(0)
        self.total_label.setText(f"TOTAL NAMES: {len(self.gamertags)}")
        self.valid_label.setText("VALID: 0")
        self.invalid_label.setText("INVALID: 0")
        self.status_label.setText(f"{len(self.gamertags)} names ready to check.")

    def check_names(self):
        if not self.gamertags:
            self.status_label.setText("No names imported. Visit Import first.")
            return

        self.results = validate_gamertags(self.gamertags)
        records = []
        valid_count = 0
        invalid_count = 0
        self.table.setRowCount(len(self.results))

        for row, result in enumerate(self.results):
            if result.status == ValidationStatus.VALID:
                status_text = "VALID"
                valid_count += 1
            else:
                status_text = "INVALID"
                invalid_count += 1

            reason = result.reason or result.note or "No issues found."
            records.append({
                "gamertag": result.gamertag,
                "status": status_text,
                "reason": reason
            })

            self.table.setItem(row, 0, QTableWidgetItem(result.gamertag))
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(
                __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                    "#62C98A" if status_text == "VALID" else "#E46B6B"
                )
            )
            self.table.setItem(row, 1, status_item)
            self.table.setItem(row, 2, QTableWidgetItem(reason))

        self.valid_label.setText(f"VALID: {valid_count}")
        self.invalid_label.setText(f"INVALID: {invalid_count}")
        self.total_label.setText(f"TOTAL NAMES: {len(self.results)}")
        self.status_label.setText(
            f"Finished checking {len(self.results)} names. Xbox availability has not been checked."
        )

        if self.results_updated_callback:
            self.results_updated_callback(records)

        self.filter_results(self.search_input.text())

    def filter_results(self, search_text):
        search_text = search_text.casefold()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            self.table.setRowHidden(
                row,
                not item or search_text not in item.text().casefold()
            )
