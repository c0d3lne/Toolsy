import random
import string

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QListWidget,
    QListWidgetItem, QMessageBox, QApplication
)


class NameGeneratorPage(QWidget):

    names_ready_for_checker = Signal(list)

    def __init__(self):
        super().__init__()

        self.generated_names = []

        self.clean_words = [
            "Shadow", "Velvet", "Hollow", "Phantom",
            "Silver", "Frozen", "Crystal", "Silent",
            "Raven", "Storm", "Echo", "Ghost",
            "Midnight", "Vortex", "Frost", "Venom",
            "Orbit", "Nova", "Solar", "Cipher",
            "Havoc", "Royal", "Scarlet", "Obsidian",
            "Blaze", "Arctic", "Legend", "Mystic"
        ]

        self.short_names = [
            "Nexo", "Vex", "Niro", "Zeno",
            "Kyro", "Rivo", "Zyro", "Aero",
            "Kova", "Raze", "Viro", "Xeno",
            "Navi", "Zavi", "Ryn", "Kiro",
            "Luno", "Vano", "Zora", "Aven",
            "Nyx", "Koda", "Rex"
        ]

        self.leet_words = [
            "tool", "next", "nitr", "ghost",
            "shadow", "venom", "cyber", "zero",
            "elite", "vortex", "hacker", "frost",
            "storm", "phantom", "reaper", "pixel"
        ]

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)

        title = QLabel("Name Generator")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Generate unique names using different styles."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QHBoxLayout()

        self.category = QComboBox()
        self.category.addItems([
            "4 Letter",
            "Clean",
            "Short",
            "Leetspeak"
        ])
        self.category.setMinimumHeight(40)

        self.amount = QSpinBox()
        self.amount.setRange(1, 500)
        self.amount.setValue(25)
        self.amount.setMinimumHeight(40)

        generate_button = QPushButton("Generate Names")
        generate_button.setMinimumHeight(40)
        generate_button.clicked.connect(self.generate_names)

        controls.addWidget(QLabel("Category"))
        controls.addWidget(self.category)
        controls.addWidget(QLabel("Quantity"))
        controls.addWidget(self.amount)
        controls.addWidget(generate_button)

        layout.addLayout(controls)

        results_heading = QLabel("Generated Names")
        results_heading.setObjectName("sectionTitle")

        layout.addWidget(results_heading)

        self.results_list = QListWidget()

        self.results_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )

        layout.addWidget(self.results_list)

        buttons = QHBoxLayout()

        copy_selected = QPushButton("Copy Selected")
        copy_selected.clicked.connect(self.copy_selected)

        copy_all = QPushButton("Copy All")
        copy_all.clicked.connect(self.copy_all)

        self.send_to_checker_button = QPushButton("Send to Name Checker")
        self.send_to_checker_button.setEnabled(False)
        self.send_to_checker_button.clicked.connect(self.send_to_checker)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_results)

        buttons.addWidget(copy_selected)
        buttons.addWidget(copy_all)
        buttons.addWidget(self.send_to_checker_button)
        buttons.addWidget(clear_button)

        layout.addLayout(buttons)

    def create_name(self, category):

        if category == "4 Letter":
            return "".join(
                random.choices(string.ascii_lowercase, k=4)
            )

        elif category == "Clean":
            return random.choice(self.clean_words)

        elif category == "Short":
            return random.choice(self.short_names)

        elif category == "Leetspeak":

            word = random.choice(self.leet_words)

            substitutions = {
                "a": "4",
                "e": "3",
                "i": "1",
                "o": "0",
                "s": "5",
                "t": "7"
            }

            result = ""

            for character in word:
                if character in substitutions and random.random() < 0.8:
                    result += substitutions[character]
                else:
                    result += character

            return result

        return ""

    def generate_names(self):

        category = self.category.currentText()
        quantity = self.amount.value()

        self.generated_names = []
        self.results_list.clear()

        attempts = 0
        maximum_attempts = quantity * 20

        while (
            len(self.generated_names) < quantity
            and attempts < maximum_attempts
        ):

            name = self.create_name(category)

            if name.lower() not in [
                existing.lower() for existing in self.generated_names
            ]:
                self.generated_names.append(name)

            attempts += 1

        for name in self.generated_names:
            self.results_list.addItem(QListWidgetItem(name))
        self.send_to_checker_button.setEnabled(bool(self.generated_names))

    def send_to_checker(self):
        if self.generated_names:
            self.names_ready_for_checker.emit(list(self.generated_names))

    def copy_selected(self):

        selected = self.results_list.selectedItems()

        if not selected:
            QMessageBox.information(
                self,
                "Nothing Selected",
                "Select at least one name first."
            )
            return

        names = "\n".join(
            item.text() for item in selected
        )

        QApplication.clipboard().setText(names)

        QMessageBox.information(
            self,
            "Copied",
            f"Copied {len(selected)} names to clipboard."
        )

    def copy_all(self):

        if not self.generated_names:
            QMessageBox.information(
                self,
                "No Names",
                "Generate some names first."
            )
            return

        QApplication.clipboard().setText(
            "\n".join(self.generated_names)
        )

        QMessageBox.information(
            self,
            "Copied",
            f"Copied {len(self.generated_names)} names to clipboard."
        )

    def clear_results(self):

        self.generated_names.clear()
        self.results_list.clear()
        self.send_to_checker_button.setEnabled(False)
