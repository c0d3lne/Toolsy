from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
    QPlainTextEdit,
)


from toolsy_core.importer import (
    import_gamertags,
    GamertagImportError,
)


class ImportPage(QWidget):

    names_imported = Signal(list)
    names_ready_for_checker = Signal(list)

    def __init__(self):
        super().__init__()

        self.gamertags = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(20)

        heading = QLabel("Import")
        heading.setObjectName("pageTitle")

        subtitle = QLabel(
            "Paste generated gamertags or import a TXT list, then send them to the Name Checker."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(18)

        title = QLabel("Import Gamertag List")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Paste one name per line, or select a UTF-8 TXT file. Names are trimmed and duplicates are skipped."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)

        self.paste_input = QPlainTextEdit()
        self.paste_input.setPlaceholderText("Paste generated gamertags here, one per line...")
        self.paste_input.setMinimumHeight(150)
        self.paste_input.setMaximumHeight(210)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("mutedText")

        self.import_button = QPushButton("Select TXT File")
        self.import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_button.clicked.connect(self.select_file)

        self.paste_button = QPushButton("Import Pasted Names")
        self.paste_button.clicked.connect(self.import_pasted)

        self.send_button = QPushButton("Send to Name Checker")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_to_checker)

        self.status_label = QLabel("Paste names or choose a TXT file to get started.")
        self.status_label.setObjectName("mutedText")
        self.status_label.setWordWrap(True)

        panel_layout.addWidget(title)
        panel_layout.addWidget(description)
        panel_layout.addWidget(self.paste_input)
        paste_actions = QHBoxLayout()
        paste_actions.addWidget(self.paste_button)
        paste_actions.addStretch()
        panel_layout.addLayout(paste_actions)
        panel_layout.addSpacing(6)
        panel_layout.addWidget(self.file_label)
        file_actions = QHBoxLayout()
        file_actions.addWidget(self.import_button)
        file_actions.addWidget(self.send_button)
        file_actions.addStretch()
        panel_layout.addLayout(file_actions)
        panel_layout.addWidget(self.status_label)

        layout.addWidget(panel)
        layout.addStretch()

    def _merge_names(self, raw_names):
        existing = {name.casefold() for name in self.gamertags}
        added = []
        duplicates = 0
        blanks = 0
        for raw_name in raw_names:
            name = str(raw_name).strip()
            if not name:
                blanks += 1
                continue
            key = name.casefold()
            if key in existing:
                duplicates += 1
                continue
            existing.add(key)
            added.append(name)
        if added:
            self.gamertags.extend(added)
            self.names_imported.emit(list(self.gamertags))
            self.send_button.setEnabled(True)
        return len(added), duplicates, blanks

    def import_pasted(self):
        pasted = self.paste_input.toPlainText().replace(",", "\n")
        if not pasted.strip():
            self.status_label.setText("Paste one or more names before importing.")
            return
        added, duplicates, blanks = self._merge_names(pasted.splitlines())
        self.status_label.setText(
            f"Pasted import complete. Added: {added}  |  Duplicates skipped: {duplicates}  |  Blank lines ignored: {blanks}  |  Total names: {len(self.gamertags)}"
        )

    def send_to_checker(self):
        if self.gamertags:
            self.names_ready_for_checker.emit(list(self.gamertags))

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Gamertag File",
            "",
            "Text Files (*.txt)",
        )
        if not file_path:
            return

        self.file_label.setText(Path(file_path).name)
        try:
            result = import_gamertags(file_path, existing_names=self.gamertags)
            self.gamertags.extend(result.gamertags)
            if result.gamertags:
                self.names_imported.emit(list(self.gamertags))
                self.send_button.setEnabled(True)
            self.status_label.setText(
                f"File import complete. Added: {result.imported_count}  |  "
                f"Duplicates skipped: {result.duplicates_skipped}  |  "
                f"Blank lines ignored: {result.blank_lines_ignored}  |  "
                f"Total names: {len(self.gamertags)}"
            )
        except GamertagImportError as error:
            self.status_label.setText(f"Import failed: {error}")
