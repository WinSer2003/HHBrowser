import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile
from PyQt5.QtGui import QIcon
import lists
endwithls = lists.endwithls
class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize attributes
        self.search_engine = "https://www.duckduckgo.com"
        self.homepage = "https://start.duckduckgo.com"
        self.download_folder = os.path.expanduser("~")  # Default download location

        # Tab widget, allows multiple tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_title)
        self.setCentralWidget(self.tabs)

        # Address bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText("Enter URL and press Enter")

        # Navigation toolbar
        navbar = QToolBar()
        self.addToolBar(navbar)
              # Back button
        self.back_btn = QAction(QIcon("icons/back.png"), 'Back', self)
        self.back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(self.back_btn)

        # Forward button
        self.forward_btn = QAction(QIcon("icons/forward.png"), 'Forward', self)
        self.forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(self.forward_btn)

        # Reload button
        self.reload_btn = QAction(QIcon("icons/reload.png"), 'Reload', self)
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(self.reload_btn)
        # Home button
        self.home_btn = QAction(QIcon("icons/home.png"), 'Home', self)
        self.home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(self.home_btn)
        self.new_btn = QAction(QIcon("icons/new.png"), 'New tab', self)
        self.new_btn.triggered.connect(lambda:         self.add_new_tab(QUrl(self.homepage), "New Tab"))
        navbar.addAction(self.new_btn)
        # Add address bar to navigation toolbar
        navbar.addWidget(self.url_bar)
        
        # SSL Icon - Removed
        # self.ssl_icon_label = QLabel()
        # self.ssl_icon_label.setPixmap(QIcon("icons/no_ssl.png").pixmap(16, 16))  # Default No Certificate
        # self.ssl_icon_label.setToolTip("No Certificate")
        # navbar.addWidget(self.ssl_icon_label)

        # Add new tab with homepage
        self.load_settings()
        self.add_new_tab(QUrl(self.homepage), "New Tab")

        # Blocklist to store blocked domains
        self.blocklist = []
        self.load_blocklist()

        # Show browser window maximized
        self.showMaximized()

        # Menu bar
        self.create_menu()

        # Enable rounded design
        self.enable_rounded_design()

    def load_blocklist(self):
        # Load the blocklist from a file (blocklist.txt)
        if os.path.exists("blocklist.txt"):
            with open("blocklist.txt", "r") as f:
                self.blocklist = [line.strip() for line in f.readlines()]

    def load_settings(self):
        # Load settings from JSON file
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.search_engine = settings.get("search_engine", self.search_engine)
                self.homepage = settings.get("homepage", self.homepage)

    def save_settings(self):
        # Save settings to JSON file
        settings = {
            "search_engine": self.search_engine,
            "homepage": self.homepage
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http" or "https"):
            if "www" in url:
                url = f"http://{url}"
            elif url.endswith(endwithls):
                url = f"https://{url}"
            else:
                url = f"{self.search_engine}/?q={url}"
        # Check if URL is in blocklist
        domain = QUrl(url).host()
        if domain in self.blocklist:
            QMessageBox.critical(self, "Blocked", f"Access to {domain} is blocked by security settings. \n Filter: Url on blockatulla listalla")
            return
       
        # Proceed with loading the URL
        self.tabs.currentWidget().setUrl(QUrl(url))

    def add_new_tab(self, qurl=None, label="Blank"):
        browser = QWebEngineView()
        browser.setUrl(qurl if qurl else QUrl(self.search_engine))

        # Removed SSL error handling and SSL status checks

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # Download listener
        profile = browser.page().profile()
        profile.downloadRequested.connect(self.handle_download)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def create_menu(self):
        # Menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # New tab
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_blank_tab)
        file_menu.addAction(new_tab_action)

        # Exit application
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")

        # Open settings
        settings_action = QAction("Open Settings", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        # Downloads menu
        downloads_menu = menubar.addMenu("Downloads")

        # Choose download folder
        download_action = QAction("Choose Download Folder", self)
        download_action.triggered.connect(self.choose_download_folder)
        downloads_menu.addAction(download_action)

        # View menu for "View Source"
        view_menu = menubar.addMenu("View")
        
        # View Source action
        view_source_action = QAction("View Source", self)
        view_source_action.triggered.connect(self.view_source)
        view_menu.addAction(view_source_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        # Clear cache
        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self.clear_cache)
        tools_menu.addAction(clear_cache_action)

        # Fullscreen mode
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        tools_menu.addAction(fullscreen_action)

    def add_blank_tab(self):
        self.add_new_tab(QUrl(self.search_engine), "New Tab")

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(self.homepage))

    def open_settings(self):
        # Create a simple settings dialog
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_layout = QVBoxLayout()

        # Search engine URL
        self.search_engine_input = QLineEdit(self.search_engine)
        settings_layout.addWidget(QLabel("Search Engine URL:"))
        settings_layout.addWidget(self.search_engine_input)

        # Homepage URL
        self.homepage_input = QLineEdit(self.homepage)
        settings_layout.addWidget(QLabel("Homepage URL:"))
        settings_layout.addWidget(self.homepage_input)

        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_settings_from_dialog)
        settings_layout.addWidget(save_btn)

        settings_dialog.setLayout(settings_layout)
        settings_dialog.exec_()




    def save_settings_from_dialog(self):
        self.search_engine = self.search_engine_input.text()
        self.homepage = self.homepage_input.text()
        self.save_settings()

    def choose_download_folder(self):
        # Open file dialog and select download folder
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_folder)
        if folder:
            self.download_folder = folder

    def handle_download(self, download_item: QWebEngineDownloadItem):
        # Handle download request
        suggested_name = download_item.suggestedFileName()
        download_path = os.path.join(self.download_folder, suggested_name)

        # Choose destination path using FileDialog
        download_dialog = QFileDialog(self)
        download_dialog.setDefaultSuffix(suggested_name.split('.')[-1])
        path, _ = download_dialog.getSaveFileName(self, "Save File As", download_path)

        if path:
            download_item.setPath(path)
            download_item.accept()

    def enable_rounded_design(self):
        # Rounded and modern style for the entire UI
        rounded_style = """
            QMainWindow {
                background-color: #2E2E2E;
                color: white;
            }
            QToolBar {
                background-color: #3A3A3A;
                color: white;
                border: none;
            }
            QTabWidget::pane {
                border: none;
                background-color: #2E2E2E;
            }
            QTabBar::tab {
                background: #505050;
                color: white;
                padding: 10px;
                margin: 2px;
                border: none;
                border-radius: 15px;
            }
            QTabBar::tab:selected {
                background: #404040;
            }
            QLineEdit {
                background-color: #3A3A3A;
                color: white;
                padding: 8px;
                border: 2px solid #666;
                border-radius: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #009688;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QToolButton {
                background-color: #3A3A3A;
                border-radius: 50%;
                padding: 10px;
                margin: 5px;
            }
            QToolButton:hover {
                background-color: #505050;
            }
            QMenuBar {
                background-color: #2E2E2E;
                color: white;
                border: none;
            }
            QMenuBar::item {
                background-color: #2E2E2E;
                color: white;
                padding: 8px 15px;
                margin: 2px;
                border-radius: 10px;
            }
            QMenuBar::item:selected {
                background-color: #3A3A3A;
            }
            QMenu {
                background-color: #2E2E2E;
                color: white;
                border-radius: 10px;
            }
            QMenu::item {
                padding: 8px 15px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background-color: #404040;
            }
            QLabel {
                color: white;
            }
            QDialog {
                background-color: #2E2E2E;
                color: white;
                border-radius: 15px;
            }
        """
        self.setStyleSheet(rounded_style)

    def view_source(self):
        # Get the current web page
        current_browser = self.tabs.currentWidget()

        # Retrieve the HTML source and display it in a new tab
        current_browser.page().toHtml(self.display_source)

    def display_source(self, html):
        # Create a new tab for the source code
        
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        i = self.tabs.addTab(text_edit, "Source View")
        self.tabs.setCurrentIndex(i)

    def clear_cache(self):
        # Clear the cache
        QWebEngineProfile.defaultProfile().clearHttpCache()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_title(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            title = current_browser.page().title()
            self.setWindowTitle(title)

app = QApplication(sys.argv)
QApplication.setApplicationName("HHBrowser")
window = SimpleBrowser()
window.show()  # Ensure the window is shown
app.exec_()
print("erm koodin vika rivi ajettu")
