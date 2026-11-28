import json
import socket
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView, QAbstractItemView,
    QComboBox
)

PROJECT_PATH = Path(__file__).resolve().parent.parent
PROXY_FILE = PROJECT_PATH / "data" / "proxies.json"
TEST_HOST = "api.ipify.org"
TEST_PORT = 443
TEST_PATH = "/?format=json"
SUPPORTED_SCHEMES = {
    "http": "HTTP",
    "https": "HTTPS",
    "socks4": "SOCKS4",
    "socks4a": "SOCKS4a",
    "socks5": "SOCKS5",
    "socks5h": "SOCKS5 (remote DNS)",
}


def normalise_proxy(value):
    """Keep an explicit proxy scheme; assume HTTP when no scheme is supplied."""
    value = value.strip()
    if not value or value.startswith("#"):
        return ""
    if "://" not in value:
        value = "http://" + value
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in SUPPORTED_SCHEMES:
        raise ValueError(
            "Unsupported proxy type. Use http://, https://, socks4://, "
            "socks4a://, socks5:// or socks5h://."
        )
    if not parsed.hostname or not parsed.port:
        raise ValueError("Proxy must include a hostname/IP address and port.")
    if not (1 <= parsed.port <= 65535):
        raise ValueError("Proxy port must be between 1 and 65535.")
    return value


def proxy_protocol(proxy_url):
    return SUPPORTED_SCHEMES.get(urlsplit(proxy_url).scheme.lower(), "Unknown")


def test_http_proxy(proxy_url):
    handler = urllib.request.ProxyHandler({
        "http": proxy_url,
        "https": proxy_url,
    })
    opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(
        "https://api.ipify.org?format=json",
        headers={"User-Agent": "Toolsy-Proxy-Tester/2.0"}
    )
    with opener.open(request, timeout=10) as response:
        if response.status == 200:
            response.read(256)
            return True, "HTTPS connection successful"
        return False, f"HTTP response: {response.status}"


def test_socks_proxy(proxy_url):
    # PySocks is installed separately and loaded only for SOCKS proxy tests.
    try:
        import socks
    except ImportError:
        return False, "SOCKS support needs PySocks. Install it with: python -m pip install PySocks"

    parsed = urlsplit(proxy_url)
    scheme = parsed.scheme.lower()
    proxy_types = {
        "socks4": socks.SOCKS4,
        "socks4a": socks.SOCKS4,
        "socks5": socks.SOCKS5,
        "socks5h": socks.SOCKS5,
    }
    proxy_type = proxy_types[scheme]
    remote_dns = scheme in ("socks4a", "socks5h")
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None

    connection = socks.socksocket()
    try:
        connection.set_proxy(
            proxy_type=proxy_type,
            addr=parsed.hostname,
            port=parsed.port,
            rdns=remote_dns,
            username=username,
            password=password,
        )
        connection.settimeout(10)
        connection.connect((TEST_HOST, TEST_PORT))
        secure = ssl.create_default_context().wrap_socket(
            connection, server_hostname=TEST_HOST
        )
        request = (
            f"GET {TEST_PATH} HTTP/1.1\r\n"
            f"Host: {TEST_HOST}\r\n"
            "User-Agent: Toolsy-Proxy-Tester/2.0\r\n"
            "Connection: close\r\n\r\n"
        )
        secure.sendall(request.encode("ascii"))
        response = secure.recv(4096)
        first_line = response.split(b"\r\n", 1)[0].decode("ascii", "replace")
        if b" 200 " in response.split(b"\r\n", 1)[0]:
            return True, "HTTPS connection successful"
        return False, first_line or "No HTTP response"
    finally:
        try:
            connection.close()
        except OSError:
            pass


def test_proxy_connection(proxy_url):
    try:
        parsed = urlsplit(proxy_url)
        if parsed.scheme.lower() in ("http", "https"):
            return test_http_proxy(proxy_url)
        if parsed.scheme.lower() in ("socks4", "socks4a", "socks5", "socks5h"):
            return test_socks_proxy(proxy_url)
        return False, "Unsupported proxy protocol"
    except Exception as error:
        message = str(error).strip() or error.__class__.__name__
        return False, message[:180]


class ProxyTestWorker(QThread):
    progress = Signal(int, bool, str)
    finished_count = Signal()

    def __init__(self, proxies, indexes):
        super().__init__()
        self.proxies = proxies
        self.indexes = indexes

    def run(self):
        for index in self.indexes:
            working, message = test_proxy_connection(self.proxies[index]["address"])
            self.progress.emit(index, working, message)
        self.finished_count.emit()


class ProxyManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.proxies = []
        self.worker = None
        self._rotation_index = -1
        self.current_proxy = None
        self.load_proxies()
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Proxy Manager")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Manage HTTP, HTTPS, SOCKS4 and SOCKS5 proxies. "
            "Proxies are stored locally. Select Next Working Proxy to rotate through tested proxies; name checks are currently offline."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        stats = QHBoxLayout()
        self.total_label = self.make_stat(stats, "TOTAL")
        self.working_label = self.make_stat(stats, "WORKING")
        self.failed_label = self.make_stat(stats, "FAILED")
        self.untested_label = self.make_stat(stats, "UNTESTED")
        layout.addLayout(stats)

        add_panel = QFrame()
        add_panel.setObjectName("panel")
        add_layout = QVBoxLayout(add_panel)
        add_layout.setContentsMargins(18, 15, 18, 15)
        add_layout.setSpacing(9)
        add_title = QLabel("ADD PROXIES")
        add_title.setObjectName("sectionTitle")
        add_layout.addWidget(add_title)

        entry_row = QHBoxLayout()
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText(
            "scheme://host:port  |  e.g. socks5://user:pass@127.0.0.1:1080"
        )
        self.proxy_input.returnPressed.connect(self.add_proxy)
        add_button = QPushButton("Add Proxy")
        add_button.clicked.connect(self.add_proxy)
        import_button = QPushButton("Import TXT")
        import_button.clicked.connect(self.import_proxies)
        entry_row.addWidget(self.proxy_input, 1)
        entry_row.addWidget(add_button)
        entry_row.addWidget(import_button)
        add_layout.addLayout(entry_row)
        rotation_row = QHBoxLayout()
        self.next_proxy_button = QPushButton("Next Working Proxy")
        self.next_proxy_button.clicked.connect(self.select_next_working_proxy)
        self.current_proxy_label = QLabel("Current proxy: none selected")
        self.current_proxy_label.setObjectName("mutedText")
        rotation_row.addWidget(self.next_proxy_button)
        rotation_row.addWidget(self.current_proxy_label, 1)
        add_layout.addLayout(rotation_row)

        hint = QLabel(
            "Supported prefixes: http://, https://, socks4://, socks4a://, socks5:// and socks5h://. "
            "Lines without a prefix are treated as HTTP."
        )
        hint.setObjectName("mutedText")
        hint.setWordWrap(True)
        add_layout.addWidget(hint)
        layout.addWidget(add_panel)

        list_panel = QFrame()
        list_panel.setObjectName("panel")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(18, 15, 18, 15)
        list_layout.setSpacing(10)

        list_title = QLabel("SAVED PROXIES")
        list_title.setObjectName("sectionTitle")
        list_layout.addWidget(list_title)

        filter_row = QHBoxLayout()
        filter_label = QLabel("Protocol filter:")
        filter_label.setObjectName("mutedText")
        self.protocol_filter = QComboBox()
        self.protocol_filter.addItems([
            "All Protocols", "HTTP", "HTTPS", "SOCKS4", "SOCKS4a",
            "SOCKS5", "SOCKS5 (remote DNS)"
        ])
        self.protocol_filter.currentIndexChanged.connect(self.refresh_table)
        self.test_filtered_button = QPushButton("Test Filtered")
        self.test_filtered_button.clicked.connect(self.test_filtered)
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.protocol_filter)
        filter_row.addStretch()
        filter_row.addWidget(self.test_filtered_button)
        list_layout.addLayout(filter_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Proxy Address", "Protocol", "Status", "Last Test"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for column in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        list_layout.addWidget(self.table, 1)

        row_one = QHBoxLayout()
        self.test_all_button = QPushButton("Test All")
        self.test_all_button.clicked.connect(self.test_all)
        self.test_selected_button = QPushButton("Test Selected")
        self.test_selected_button.clicked.connect(self.test_selected)
        row_one.addWidget(self.test_all_button)
        row_one.addWidget(self.test_selected_button)
        row_one.addStretch()
        list_layout.addLayout(row_one)

        row_two = QHBoxLayout()
        remove_broken = QPushButton("Remove Broken Proxies")
        remove_broken.clicked.connect(self.remove_broken)
        remove_selected = QPushButton("Remove Selected")
        remove_selected.clicked.connect(self.remove_selected)
        clear_all = QPushButton("Clear All")
        clear_all.clicked.connect(self.clear_all)
        row_two.addWidget(remove_broken)
        row_two.addWidget(remove_selected)
        row_two.addStretch()
        row_two.addWidget(clear_all)
        list_layout.addLayout(row_two)

        self.status_label = QLabel(
            "Ready. Testing checks an HTTPS connection to api.ipify.org. "
            "A successful test does not guarantee compatibility with every website."
        )
        self.status_label.setObjectName("mutedText")
        self.status_label.setWordWrap(True)
        list_layout.addWidget(self.status_label)
        layout.addWidget(list_panel, 1)

    def make_stat(self, parent, heading):
        card = QFrame()
        card.setObjectName("statCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(13, 10, 13, 10)
        heading_label = QLabel(heading)
        heading_label.setObjectName("statHeading")
        value = QLabel("0")
        value.setObjectName("statValue")
        card_layout.addWidget(heading_label)
        card_layout.addWidget(value)
        parent.addWidget(card)
        return value

    def select_next_working_proxy(self):
        working = [p for p in self.proxies if p.get("status") == "WORKING"]
        if not working:
            self.current_proxy = None
            self.current_proxy_label.setText("Current proxy: no tested working proxies")
            self.status_label.setText("Test proxies first. Only proxies marked WORKING are included in rotation.")
            return None
        self._rotation_index = (self._rotation_index + 1) % len(working)
        self.current_proxy = working[self._rotation_index]["address"]
        self.current_proxy_label.setText(f"Current proxy: {self.current_proxy}")
        self.status_label.setText(f"Selected proxy {self._rotation_index + 1} of {len(working)} working proxies.")
        return self.current_proxy

    def get_next_working_proxy(self):
        """Return the next tested working proxy for a future network consumer."""
        working = [p for p in self.proxies if p.get("status") == "WORKING"]
        if not working:
            return None
        self._rotation_index = (self._rotation_index + 1) % len(working)
        self.current_proxy = working[self._rotation_index]["address"]
        return self.current_proxy

    def load_proxies(self):
        if not PROXY_FILE.exists():
            self.proxies = []
            return
        try:
            data = json.loads(PROXY_FILE.read_text(encoding="utf-8"))
            self.proxies = data if isinstance(data, list) else []
            self.proxies = [
                item for item in self.proxies
                if isinstance(item, dict) and item.get("address")
            ]
            for item in self.proxies:
                item.setdefault("status", "UNTESTED")
                item.setdefault("last_test", "Never")
                item.setdefault("message", "")
        except (OSError, json.JSONDecodeError):
            self.proxies = []

    def save_proxies(self):
        PROXY_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary = PROXY_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.proxies, indent=4), encoding="utf-8")
        temporary.replace(PROXY_FILE)

    def visible_proxy_indexes(self):
        selected_protocol = self.protocol_filter.currentText()
        return [
            index for index, proxy in enumerate(self.proxies)
            if selected_protocol == "All Protocols"
            or proxy_protocol(proxy["address"]) == selected_protocol
        ]

    def refresh_table(self):
        indexes = self.visible_proxy_indexes() if hasattr(self, "protocol_filter") else list(range(len(self.proxies)))
        self.table.setRowCount(len(indexes))
        counts = {"WORKING": 0, "FAILED": 0, "UNTESTED": 0}
        for row, index in enumerate(indexes):
            proxy = self.proxies[index]
            status = proxy.get("status", "UNTESTED")
            if status not in counts:
                status = "UNTESTED"
                proxy["status"] = status
            counts[status] += 1
            values = [
                proxy.get("address", ""),
                proxy_protocol(proxy.get("address", "")),
                status.title(),
                proxy.get("last_test", "Never"),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if column == 0:
                    item.setToolTip(proxy.get("message", ""))
                self.table.setItem(row, column, item)
        self.total_label.setText(str(len(self.proxies)))
        self.working_label.setText(str(sum(p.get("status") == "WORKING" for p in self.proxies)))
        self.failed_label.setText(str(sum(p.get("status") == "FAILED" for p in self.proxies)))
        self.untested_label.setText(str(sum(p.get("status", "UNTESTED") == "UNTESTED" for p in self.proxies)))

    def add_proxy(self):
        try:
            address = normalise_proxy(self.proxy_input.text())
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Proxy", str(error))
            return
        if not address:
            return
        if any(item["address"].lower() == address.lower() for item in self.proxies):
            QMessageBox.information(self, "Already Added", "That proxy is already saved.")
            return
        self.proxies.append({
            "address": address, "status": "UNTESTED",
            "last_test": "Never", "message": ""
        })
        self.proxy_input.clear()
        self.save_proxies()
        self.refresh_table()

    def import_proxies(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Proxy List", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            content = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(self, "Import Failed", str(error))
            return
        existing = {item["address"].lower() for item in self.proxies}
        added, skipped = 0, 0
        invalid = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                address = normalise_proxy(line)
            except ValueError as error:
                invalid.append(f"Line {line_number}: {error}")
                skipped += 1
                continue
            if address.lower() in existing:
                skipped += 1
                continue
            self.proxies.append({
                "address": address, "status": "UNTESTED",
                "last_test": "Never", "message": ""
            })
            existing.add(address.lower())
            added += 1
        self.save_proxies()
        self.refresh_table()
        summary = f"Imported {added} proxy/proxies. Skipped {skipped} duplicate or invalid line(s)."
        if invalid:
            summary += "\n\nFirst invalid entries:\n" + "\n".join(invalid[:8])
        QMessageBox.information(self, "Import Complete", summary)

    def selected_indexes(self):
        visible = self.visible_proxy_indexes()
        rows = {item.row() for item in self.table.selectionModel().selectedRows()}
        return sorted(visible[row] for row in rows if row < len(visible))

    def test_all(self):
        self.start_testing(list(range(len(self.proxies))))

    def test_filtered(self):
        self.start_testing(self.visible_proxy_indexes())

    def test_selected(self):
        indexes = self.selected_indexes()
        if not indexes:
            QMessageBox.information(self, "Select Proxies", "Select one or more proxies first.")
            return
        self.start_testing(indexes)

    def start_testing(self, indexes):
        if self.worker and self.worker.isRunning():
            return
        if not indexes:
            self.status_label.setText("There are no matching proxies to test.")
            return
        self.test_all_button.setEnabled(False)
        self.test_selected_button.setEnabled(False)
        self.test_filtered_button.setEnabled(False)
        self.status_label.setText(f"Testing {len(indexes)} proxy/proxies...")
        self.worker = ProxyTestWorker(self.proxies, indexes)
        self.worker.progress.connect(self.update_test_result)
        self.worker.finished_count.connect(self.testing_finished)
        self.worker.start()

    def update_test_result(self, index, working, message):
        if index >= len(self.proxies):
            return
        proxy = self.proxies[index]
        proxy["status"] = "WORKING" if working else "FAILED"
        proxy["message"] = message
        proxy["last_test"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_proxies()
        self.refresh_table()

    def testing_finished(self):
        self.test_all_button.setEnabled(True)
        self.test_selected_button.setEnabled(True)
        self.test_filtered_button.setEnabled(True)
        self.status_label.setText("Proxy testing finished.")
        self.save_proxies()
        self.refresh_table()

    def remove_broken(self):
        broken = [item for item in self.proxies if item.get("status") == "FAILED"]
        if not broken:
            QMessageBox.information(self, "No Broken Proxies", "There are no failed proxies to remove.")
            return
        answer = QMessageBox.question(
            self, "Remove Broken Proxies",
            f"Remove {len(broken)} failed proxy/proxies? Working and untested proxies will be kept.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.proxies = [item for item in self.proxies if item.get("status") != "FAILED"]
        self.save_proxies()
        self.refresh_table()
        self.status_label.setText(f"Removed {len(broken)} failed proxy/proxies.")

    def remove_selected(self):
        indexes = set(self.selected_indexes())
        if not indexes:
            QMessageBox.information(self, "Select Proxies", "Select proxies to remove first.")
            return
        answer = QMessageBox.question(
            self, "Remove Selected",
            f"Remove {len(indexes)} selected proxy/proxies?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.proxies = [p for i, p in enumerate(self.proxies) if i not in indexes]
        self.save_proxies()
        self.refresh_table()

    def clear_all(self):
        if not self.proxies:
            return
        answer = QMessageBox.question(
            self, "Clear All Proxies", "Permanently remove every saved proxy?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.proxies = []
        self.save_proxies()
        self.refresh_table()
        self.status_label.setText("All saved proxies have been cleared.")
