import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QFileDialog,
    QMessageBox, QComboBox, QInputDialog, QAbstractItemView,
)

PROJECT_PATH = Path(__file__).resolve().parent.parent
WATCHLIST_FILE = PROJECT_PATH / "data" / "watchlist.json"
STATUSES = ("UNKNOWN", "AVAILABLE", "TAKEN")


class WatchlistPage(QWidget):
    """Locally stored watchlist. Status changes here are manual only."""

    def __init__(self):
        super().__init__()
        self.names = self.load_names()
        self.build_ui()
        self.refresh_table()
        # Alerts are shown when the user opens the Watchlist page.

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(14)

        title = QLabel("Watchlist")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Save gamertags and record status changes locally.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        stats = QHBoxLayout()
        self.total_value = self.make_stat(stats, "TOTAL WATCHED")
        self.available_value = self.make_stat(stats, "AVAILABLE")
        self.taken_value = self.make_stat(stats, "TAKEN")
        self.unknown_value = self.make_stat(stats, "UNKNOWN")
        layout.addLayout(stats)

        add_panel = QFrame()
        add_panel.setObjectName("panel")
        add_layout = QVBoxLayout(add_panel)
        add_layout.setContentsMargins(16, 13, 16, 13)
        add_layout.setSpacing(8)
        add_title = QLabel("ADD GAMERTAGS")
        add_title.setObjectName("sectionTitle")
        add_layout.addWidget(add_title)
        row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter one or more names, separated by commas or new lines")
        self.name_input.returnPressed.connect(self.add_names)
        row.addWidget(self.name_input, 1)
        add_button = QPushButton("Add Names")
        add_button.clicked.connect(self.add_names)
        import_button = QPushButton("Import TXT")
        import_button.clicked.connect(self.import_names)
        row.addWidget(add_button)
        row.addWidget(import_button)
        add_layout.addLayout(row)
        layout.addWidget(add_panel)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 13, 16, 13)
        panel_layout.setSpacing(9)
        title_row = QHBoxLayout()
        section = QLabel("SAVED NAMES")
        section.setObjectName("sectionTitle")
        title_row.addWidget(section)
        title_row.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search gamertags...")
        self.search_input.textChanged.connect(self.refresh_table)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Names", "Available", "Taken", "Unknown"])
        self.status_filter.currentIndexChanged.connect(self.refresh_table)
        title_row.addWidget(self.search_input)
        title_row.addWidget(self.status_filter)
        panel_layout.addLayout(title_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "GAMERTAG", "CURRENT STATUS", "PREVIOUS STATUS", "LAST CHECKED", "CHECKS"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(lambda _r, _c: self.view_history())
        panel_layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        for label, handler in (
            ("Set Manual Status", self.set_manual_status),
            ("View History", self.view_history),
            ("Remove Selected", self.remove_selected),
            ("Refresh", self.refresh_table),
        ):
            button = QPushButton(label)
            button.clicked.connect(handler)
            actions.addWidget(button)
        actions.addStretch()
        clear_button = QPushButton("Clear Watchlist")
        clear_button.clicked.connect(self.clear_watchlist)
        actions.addWidget(clear_button)
        panel_layout.addLayout(actions)

        self.notice = QLabel(
            "Manual records only. Xbox availability checking and background monitoring are not connected."
        )
        self.notice.setObjectName("mutedText")
        self.notice.setWordWrap(True)
        panel_layout.addWidget(self.notice)
        layout.addWidget(panel, 1)

    def make_stat(self, parent, heading):
        card = QFrame()
        card.setObjectName("statCard")
        box = QVBoxLayout(card)
        box.setContentsMargins(13, 9, 13, 9)
        head = QLabel(heading)
        head.setObjectName("statHeading")
        value = QLabel("0")
        value.setObjectName("statValue")
        box.addWidget(head)
        box.addWidget(value)
        parent.addWidget(card)
        return value

    @staticmethod
    def now():
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def load_names(self):
        try:
            raw = json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []
        names, seen = [], set()
        for item in raw:
            if not isinstance(item, dict):
                continue
            tag = str(item.get("gamertag", "")).strip()
            key = tag.casefold()
            if not tag or key in seen:
                continue
            seen.add(key)
            status = str(item.get("status", "UNKNOWN")).upper()
            if status not in STATUSES:
                status = "UNKNOWN"
            history = item.get("history", [])
            try:
                checks = max(0, int(item.get("checks", 0) or 0))
            except (TypeError, ValueError):
                checks = 0
            names.append({
                "gamertag": tag,
                "status": status,
                "previous_status": item.get("previous_status"),
                "last_checked": item.get("last_checked", ""),
                "checks": checks,
                "history": history if isinstance(history, list) else [],
                "alert_generated": bool(item.get("alert_generated", False)),
                "alert_seen": bool(item.get("alert_seen", True)),
            })
        return names

    def save_names(self):
        WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp = WATCHLIST_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(self.names, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(WATCHLIST_FILE)

    def add_names(self):
        parts = self.name_input.text().replace(",", "\n").splitlines()
        self._add_names(parts)
        self.name_input.clear()

    def _add_names(self, parts):
        existing = {x["gamertag"].casefold() for x in self.names}
        added = 0
        for value in parts:
            tag = value.strip()
            if not tag or tag.casefold() in existing:
                continue
            existing.add(tag.casefold())
            self.names.append({
                "gamertag": tag, "status": "UNKNOWN", "previous_status": None,
                "last_checked": "", "checks": 0, "history": [],
                "alert_generated": False, "alert_seen": True,
            })
            added += 1
        if added:
            self.save_names()
        self.refresh_table()
        if added:
            self.notice.setText(f"Added {added} name(s). Statuses remain unknown until manually recorded.")

    def import_names(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Gamertags", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(self, "Import Failed", str(error))
            return
        before = len(self.names)
        self._add_names(text.replace(",", "\n").splitlines())
        QMessageBox.information(self, "Import Complete", f"Added {len(self.names) - before} new name(s). Duplicates were skipped.")

    def refresh_table(self, *_):
        if not hasattr(self, "table"):
            return
        query = self.search_input.text().strip().casefold()
        chosen = self.status_filter.currentText().upper().replace(" NAMES", "")
        shown = [n for n in self.names if query in n["gamertag"].casefold()
                 and (chosen == "ALL" or n["status"] == chosen)]
        self.table.setRowCount(len(shown))
        colors = {"AVAILABLE": "#62C98A", "TAKEN": "#E46B6B", "UNKNOWN": "#AAAAAA"}
        for row, record in enumerate(shown):
            previous = record.get("previous_status") or "—"
            values = [record["gamertag"], f'{record["status"]} (MANUAL)' if record["checks"] else record["status"],
                      previous, record.get("last_checked") or "Never", str(record["checks"])]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                cell.setData(Qt.ItemDataRole.UserRole, record["gamertag"])
                if col == 1:
                    cell.setForeground(QColor(colors[record["status"]]))
                    cell.setToolTip("Manually recorded status; this is not an Xbox availability result." if record["checks"] else "No status recorded.")
                if record.get("alert_generated") and not record.get("alert_seen"):
                    cell.setBackground(QColor("#263527"))
                self.table.setItem(row, col, cell)
        self.total_value.setText(str(len(self.names)))
        self.available_value.setText(str(sum(n["status"] == "AVAILABLE" for n in self.names)))
        self.taken_value.setText(str(sum(n["status"] == "TAKEN" for n in self.names)))
        self.unknown_value.setText(str(sum(n["status"] == "UNKNOWN" for n in self.names)))

    def selected_records(self):
        tags = {self.table.item(i.row(), 0).data(Qt.ItemDataRole.UserRole)
                for i in self.table.selectionModel().selectedRows() if self.table.item(i.row(), 0)}
        return [n for n in self.names if n["gamertag"] in tags]

    def set_manual_status(self):
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "Select a Name", "Select one or more names first.")
            return
        status, ok = QInputDialog.getItem(self, "Manual Status", "Record status (manual only):", list(STATUSES), 0, False)
        if not ok:
            return
        now = self.now()
        newly_available = []
        for record in selected:
            old = record["status"]
            record["previous_status"] = old
            record["status"] = status
            record["last_checked"] = now
            record["checks"] += 1
            event = {"from": old, "to": status, "date": now, "source": "manual"}
            record["history"].append(event)
            if old == "TAKEN" and status == "AVAILABLE":
                record["alert_generated"] = True
                record["alert_seen"] = False
                newly_available.append(record["gamertag"])
        self.save_names()
        self.refresh_table()
        if newly_available:
            QMessageBox.information(self, "Manual Status Change", "Marked as AVAILABLE manually (not verified by Xbox):\n\n" + "\n".join(newly_available))
            for record in selected:
                if record["gamertag"] in newly_available:
                    record["alert_seen"] = True
            self.save_names()
            self.refresh_table()
        self.notice.setText("Status recorded manually. No Xbox availability check was performed.")

    def show_unseen_alerts(self):
        pending = [n["gamertag"] for n in self.names if n.get("alert_generated") and not n.get("alert_seen")]
        if not pending:
            return
        QMessageBox.information(self, "Watchlist Alert — Manual Record", "These names were manually changed from TAKEN to AVAILABLE (not verified by Xbox):\n\n" + "\n".join(pending))
        for record in self.names:
            if record["gamertag"] in pending:
                record["alert_seen"] = True
        self.save_names()
        self.refresh_table()

    def view_history(self):
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "Select a Name", "Select a name to view its history.")
            return
        blocks = []
        for record in selected:
            events = record.get("history", [])
            lines = [f'{e.get("date", "Unknown date")}  {e.get("from", "UNKNOWN")} → {e.get("to", "UNKNOWN")}  [{e.get("source", "manual").upper()}]'
                     for e in reversed(events[-30:]) if isinstance(e, dict)]
            blocks.append(record["gamertag"] + "\n" + ("\n".join(lines) if lines else "No status history."))
        QMessageBox.information(self, "Watchlist History", "\n\n".join(blocks))

    def remove_selected(self):
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "Select Names", "Select one or more names first.")
            return
        answer = QMessageBox.question(self, "Remove Names", f"Remove {len(selected)} selected name(s)?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        tags = {n["gamertag"] for n in selected}
        self.names = [n for n in self.names if n["gamertag"] not in tags]
        self.save_names()
        self.refresh_table()

    def clear_watchlist(self):
        if not self.names:
            return
        answer = QMessageBox.question(self, "Clear Watchlist", "Permanently remove all watched names and their history?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.names = []
        self.save_names()
        self.refresh_table()
