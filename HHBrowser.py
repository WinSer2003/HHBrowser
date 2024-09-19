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

        # New tab button
        self.new_btn = QAction(QIcon("icons/new.png"), 'New tab', self)
        self.new_btn.triggered.connect(lambda: self.add_new_tab(QUrl(self.homepage), "New Tab"))
        navbar.addAction(self.new_btn)

        # Add address bar to navigation toolbar
        navbar.addWidget(self.url_bar)

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

        # History list
        self.history_file = "history.txt"
        self.history = []
        self.load_history()

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

    def load_history(self):
        # Load history from file
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = [line.strip() for line in f.readlines()]

    def save_history(self):
        # Save history to file
        with open(self.history_file, "w") as f:
            for url in self.history:
                f.write(f"{url}\n")

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
            QMessageBox.critical(self, "Blocked", f"Access to {domain} is blocked by security settings.")
            return
        
        # Proceed with loading the URL
        self.tabs.currentWidget().setUrl(QUrl(url))
        
        # Save URL to history
        if url not in self.history:
            self.history.append(url)
            self.save_history()
    
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

        # History menu
        history_menu = menubar.addMenu("History")

        # View History action
        view_history_action = QAction("View History", self)
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        # AI Chat action
        ai_chat_action = QAction("Start AI Chat", self)
        ai_chat_action.triggered.connect(lambda: self.add_new_tab(QUrl("https://duckduckgo.com/aichat"), "AI Chat"))
        tools_menu.addAction(ai_chat_action)

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
        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        QMainWindow {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1c1f26, stop:1 #34495e);
            background-size: 200% 200%;
            animation: gradientAnimation 15s ease infinite;
            color: white;
        }

        QToolBar {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #34495e, stop:1 #2C3E50);
            color: white;
            border: none;
            border-bottom: 2px solid #1C2833;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.5);
        }

        QTabWidget::pane {
            border: none;
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1C1F26, stop:1 #2C3E50);
            background-size: 200% 200%;
            animation: gradientAnimation 20s ease infinite;
        }

        QTabBar::tab {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #3A3F4B, stop:1 #4A5060);
            color: white;
            padding: 10px;
            margin: 2px;
            border: none;
            border-radius: 15px;
            transition: background 0.3s, transform 0.3s;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.4);
        }

        QTabBar::tab:selected {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2D3A4A, stop:1 #3B4B5A);
            transform: scale(1.05);
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.6);
        }

        QLineEdit {
            background-color: #2C313C;
            color: white;
            padding: 8px;
            border: 2px solid #445566;
            border-radius: 20px;
            transition: border 0.3s, box-shadow 0.3s;
        }

        QLineEdit:focus {
            border: 2px solid #009688;
            box-shadow: 0 0 5px rgba(0, 150, 136, 0.8);
        }

        QPushButton {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4CAF50, stop:1 #45A049);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            transition: background 0.3s, transform 0.3s;
            background_transparency: 100%;
        }

        QPushButton:hover {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #43A047, stop:1 #388E3C);
            transform: translateY(-2px);
            box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.3);
        }

        QToolButton {
            background-color: #252A34;
            border-radius: 50%;
            padding: 10px;
            margin: 5px;
            transition: background-color 0.3s, transform 0.3s;
        }

        QToolButton:hover {
            background-color: #3A3F4B;
            transform: scale(1.1);
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
        }

        QMenuBar {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1c1f26, stop:1 #34495e);
            color: white;
            border: none;
            background-size: 200% 200%;
            animation: gradientAnimation 20s ease infinite;
        }

        QMenuBar::item {
            background-color: transparent;
            color: white;
            padding: 8px 15px;
            margin: 2px;
            border-radius: 10px;
            transition: background-color 0.3s, color 0.3s;
        }

        QMenuBar::item:selected {
            background-color: #2A313E;
            color: #FFFFFF;
            background_transparency: 100%;
        }

        QMenu {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1C1F26, stop:1 #2C3E50);
            color: white;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.5);
        }

        QMenu::item {
            padding: 8px 15px;
            border-radius: 8px;
            transition: background-color 0.3s;
        }

        QMenu::item:selected {
            background-color: #3B4B5A;
        }

        QLabel {
            color: white;
        }

        QDialog {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1C1F26, stop:1 #2C3E50);
            color: white;
            border-radius: 15px;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.5);
            background-size: 200% 200%;
            animation: gradientAnimation 15s ease infinite;
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

    def view_history(self):
        # Create a simple history dialog
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        history_layout = QVBoxLayout()

        # List widget for displaying history
        history_list = QListWidget()
        history_list.addItems(self.history)
        history_layout.addWidget(history_list)

        # Open URL action
        open_url_action = QPushButton("Open Selected URL", self)
        open_url_action.clicked.connect(lambda: self.open_selected_url(history_list))
        history_layout.addWidget(open_url_action)

        history_dialog.setLayout(history_layout)
        history_dialog.exec_()

    def open_selected_url(self, history_list):
        selected_items = history_list.selectedItems()
        if selected_items:
            selected_url = selected_items[0].text()
            self.tabs.currentWidget().setUrl(QUrl(selected_url))

app = QApplication(sys.argv)
QApplication.setApplicationName("HHBrowser")
window = SimpleBrowser()
window.show()  # Ensure the window is shown
app.exec_()
print("Application closed")
