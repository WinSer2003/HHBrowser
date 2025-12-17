import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QDockWidget

import lists
endwithls = lists.endwithls

class CustomWebEnginePage(QWebEnginePage):
    """Custom web engine page to add Inspect option to context menu."""
    def __init__(self, profile, browser_instance):
        super().__init__(profile)
        self.browser_instance = browser_instance

    def contextMenuEvent(self, params):
        # Create a context menu and add Inspect action
        menu = QMenu()
        
        # Add Inspect action
        inspect_action = menu.addAction("Inspect Element")
        inspect_action.triggered.connect(self.browser_instance.open_devtools)
        
        # Show the menu at cursor position
        menu.exec_(params.globalPos())

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize attributes
        self.search_engine = "https://www.duckduckgo.com"
        self.homepage = "https://start.duckduckgo.com"
        self.download_folder = os.path.expanduser("~")  # Default download location
        self.icon_pack = "default"  # Default icon pack

        # Tab widget, allows multiple tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_title)
        self.setCentralWidget(self.tabs)
        # --- DevTools Dock ---
        self.devtools_dock = QDockWidget("Developer Tools", self)
        self.devtools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.devtools_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

        self.devtools_view = QWebEngineView()
        self.devtools_dock.setWidget(self.devtools_view)

        self.addDockWidget(Qt.RightDockWidgetArea, self.devtools_dock)
        self.devtools_dock.hide()

        # Address bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText("Enter URL and press Enter")

        # Navigation toolbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Back button
        self.back_btn = QAction(self.get_icon("back.png"), 'Back', self)
        self.back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        # Shortcut: Alt+Left
        self.back_btn.setShortcut(QKeySequence("Alt+Left"))
        navbar.addAction(self.back_btn)

        # Forward button
        self.forward_btn = QAction(self.get_icon("forward.png"), 'Forward', self)
        self.forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        # Shortcut: Alt+Right
        self.forward_btn.setShortcut(QKeySequence("Alt+Right"))
        navbar.addAction(self.forward_btn)

        # Reload button
        self.reload_btn = QAction(self.get_icon("reload.png"), 'Reload', self)
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        # Shortcut: Ctrl+R
        self.reload_btn.setShortcut(QKeySequence("Ctrl+R"))
        navbar.addAction(self.reload_btn)

        # Home button
        self.home_btn = QAction(self.get_icon("home.png"), 'Home', self)
        self.home_btn.triggered.connect(self.navigate_home)
        # Shortcut: Alt+Home
        self.home_btn.setShortcut(QKeySequence("Alt+Home"))
        navbar.addAction(self.home_btn)

        # New tab button
        self.new_btn = QAction(self.get_icon("new.png"), 'New tab', self)
        self.new_btn.triggered.connect(lambda: self.add_new_tab(QUrl(self.homepage), "New Tab"))
        navbar.addAction(self.new_btn)

        # Add address bar to navigation toolbar
        navbar.addWidget(self.url_bar)

        # Shortcuts for tab navigation and actions

        # Next / Previous tab: Ctrl+Tab / Ctrl+Shift+Tab
        next_tab_sc = QShortcut(QKeySequence("Ctrl+Tab"), self)
        prev_tab_sc = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        def next_tab():
            i = self.tabs.currentIndex()
            count = self.tabs.count()
            if count > 1:
                self.tabs.setCurrentIndex((i + 1) % count)
        def prev_tab():
            i = self.tabs.currentIndex()
            count = self.tabs.count()
            if count > 1:
                self.tabs.setCurrentIndex((i - 1) % count)
        next_tab_sc.activated.connect(next_tab)
        prev_tab_sc.activated.connect(prev_tab)

        # Focus address bar: Ctrl+L
        focus_url_sc = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_url_sc.activated.connect(lambda: self.url_bar.setFocus())

        # Note: Ctrl+T handled by the menu action (application-wide)

        # Place the bookmarks toolbar on the next row below the navigation toolbar
        self.addToolBarBreak()
        self.bookmarks_toolbar = QToolBar("Bookmarks Toolbar")
        self.bookmarks_toolbar.setObjectName("BookmarksToolbar")
        self.bookmarks_toolbar.setMovable(True)
        self.addToolBar(Qt.TopToolBarArea, self.bookmarks_toolbar)

        # Add new tab with homepage
        self.load_settings()
        self.add_new_tab(QUrl(self.homepage), "New Tab")

        # Blocklist to store blocked domains
        self.blocklist = []
        self.load_blocklist()

        # Bookmarks storage
        self.bookmarks_file = "bookmarks.json"
        self.bookmarks = []
        self.load_bookmarks()
        # Show browser window maximized
        self.showMaximized()

        # Populate bookmarks toolbar
        self.refresh_bookmarks_toolbar()

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

    def get_icon(self, icon_name):
        """Get icon from the current icon pack. Falls back to default if not found."""
        if self.icon_pack != "default":
            custom_path = f"icons/packs/{self.icon_pack}/{icon_name}"
            if os.path.exists(custom_path):
                return QIcon(custom_path)
        # Fall back to default icons
        return QIcon(f"icons/{icon_name}")

    def get_available_icon_packs(self):
        """Scan and return list of available icon packs."""
        packs = ["default"]
        packs_dir = "icons/packs"
        if os.path.isdir(packs_dir):
            for item in os.listdir(packs_dir):
                item_path = os.path.join(packs_dir, item)
                if os.path.isdir(item_path):
                    packs.append(item)
        return sorted(packs)

    def load_settings(self):
        # Load settings from JSON file
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.search_engine = settings.get("search_engine", self.search_engine)
                self.homepage = settings.get("homepage", self.homepage)
                self.icon_pack = settings.get("icon_pack", self.icon_pack)
    def load_ad_blocklist(self):
    # Load ad blocklist from file (adblocklist.txt)
        self.ad_blocklist = []
        if os.path.exists("adblocklist.txt"):
         with open("adblocklist.txt", "r") as f:
            self.ad_blocklist = [line.strip() for line in f.readlines()]

    def save_settings(self):
        # Save settings to JSON file
        settings = {
            "search_engine": self.search_engine,
            "homepage": self.homepage,
            "icon_pack": self.icon_pack
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_history(self):
        # Load history from file
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = [line.strip() for line in f.readlines()]

    def load_bookmarks(self):
        # Load bookmarks from JSON file
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, "r") as f:
                    data = json.load(f)
                    # ensure list of dicts with title/url
                    if isinstance(data, list):
                        # ensure pinned flag exists
                        for bm in data:
                            if isinstance(bm, dict):
                                bm.setdefault("pinned", False)
                        self.bookmarks = data
            except Exception:
                self.bookmarks = []

    def save_bookmarks(self):
        # Save bookmarks to JSON file
        try:
            with open(self.bookmarks_file, "w") as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception:
            pass

    def refresh_bookmarks_toolbar(self):
        # Clear existing actions
        for a in list(self.bookmarks_toolbar.actions()):
            self.bookmarks_toolbar.removeAction(a)

        # Add pinned bookmarks as toolbar actions
        for bm in self.bookmarks:
            if not isinstance(bm, dict):
                continue
            if not bm.get("pinned", False):
                continue
            title = bm.get("title") or bm.get("url")
            url = bm.get("url")
            act = QAction(title, self)
            act.triggered.connect(lambda chk=False, u=url: self.open_bookmark_url(u))
            self.bookmarks_toolbar.addAction(act)

    def open_bookmark_url(self, url):
        # Open bookmark in current tab
        try:
            self.tabs.currentWidget().setUrl(QUrl(url))
        except Exception:
            pass

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
        
        # Create custom page with context menu handler
        profile = QWebEngineProfile.defaultProfile()
        custom_page = CustomWebEnginePage(profile, self)
        browser.setPage(custom_page)

        browser.setUrl(qurl if qurl else QUrl(self.search_engine))

        # Removed SSL error handling and SSL status checks

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # Download listener
        profile.downloadRequested.connect(self.handle_download)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        # Record navigations to history (captures link clicks and redirects)
        browser.urlChanged.connect(lambda qurl: self.record_history(qurl))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def create_menu(self):
        # Menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # New tab
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_blank_tab)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.setShortcutContext(Qt.ApplicationShortcut)
        file_menu.addAction(new_tab_action)

        # Close tab
        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.setShortcutContext(Qt.ApplicationShortcut)
        close_tab_action.triggered.connect(lambda: self.close_current_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_tab_action)

        # Exit application
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
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

        # View menu
        view_menu = menubar.addMenu("View")

        # Focus address bar action
        focus_addr_action = QAction("Focus Address Bar", self)
        focus_addr_action.setShortcut(QKeySequence("Ctrl+L"))
        focus_addr_action.triggered.connect(lambda: self.url_bar.setFocus())
        view_menu.addAction(focus_addr_action)

        # History menu
        history_menu = menubar.addMenu("History")

        # View History action
        view_history_action = QAction("View History", self)
        view_history_action.setShortcut(QKeySequence("Ctrl+H"))
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)

        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")

        add_book_action = QAction("Add Bookmark", self)
        add_book_action.setShortcut("Ctrl+D")
        add_book_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_book_action)

        view_bookmarks_action = QAction("View Bookmarks", self)
        view_bookmarks_action.triggered.connect(self.view_bookmarks)
        bookmarks_menu.addAction(view_bookmarks_action)

        # Show/hide bookmarks toolbar
        self.toggle_bookmarks_toolbar_action = QAction("Show Bookmarks Toolbar", self)
        self.toggle_bookmarks_toolbar_action.setCheckable(True)
        self.toggle_bookmarks_toolbar_action.setChecked(self.bookmarks_toolbar.isVisible())
        self.toggle_bookmarks_toolbar_action.triggered.connect(self.toggle_bookmarks_toolbar)
        self.toggle_bookmarks_toolbar_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        bookmarks_menu.addAction(self.toggle_bookmarks_toolbar_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        # DevTools
        devtools_action = QAction("Open DevTools", self)
        devtools_action.setShortcut("F12")
        devtools_action.triggered.connect(self.open_devtools)
        tools_menu.addAction(devtools_action)
        # Alternate DevTools shortcut (Ctrl+Shift+I)
        devtools_alt = QAction("Open DevTools (Alternate)", self)
        devtools_alt.setShortcut(QKeySequence("Ctrl+Shift+I"))
        devtools_alt.triggered.connect(self.open_devtools)
        tools_menu.addAction(devtools_alt)

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

    def record_history(self, qurl):
        """Record a navigated URL into history and persist it."""
        try:
            url = qurl.toString()
            if not url:
                return
            # Avoid duplicate entries
            if url not in self.history:
                self.history.append(url)
                self.save_history()
        except Exception:
            pass

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

        # Icon Pack Selection
        self.icon_pack_combo = QComboBox()
        available_packs = self.get_available_icon_packs()
        self.icon_pack_combo.addItems(available_packs)
        current_index = available_packs.index(self.icon_pack) if self.icon_pack in available_packs else 0
        self.icon_pack_combo.setCurrentIndex(current_index)
        settings_layout.addWidget(QLabel("Icon Pack:"))
        settings_layout.addWidget(self.icon_pack_combo)

        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_settings_from_dialog)
        settings_layout.addWidget(save_btn)

        settings_dialog.setLayout(settings_layout)
        settings_dialog.exec_()

    def save_settings_from_dialog(self):
        self.search_engine = self.search_engine_input.text()
        self.homepage = self.homepage_input.text()
        selected_pack = self.icon_pack_combo.currentText()
        if selected_pack != self.icon_pack:
            self.icon_pack = selected_pack
            self.reload_toolbar_icons()
        self.save_settings()

    def choose_download_folder(self):
        # Open file dialog and select download folder
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_folder)
        if folder:
            self.download_folder = folder

    def reload_toolbar_icons(self):
        """Reload all toolbar icons from the current icon pack."""
        self.back_btn.setIcon(self.get_icon("back.png"))
        self.forward_btn.setIcon(self.get_icon("forward.png"))
        self.reload_btn.setIcon(self.get_icon("reload.png"))
        self.home_btn.setIcon(self.get_icon("home.png"))
        self.new_btn.setIcon(self.get_icon("new.png"))

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
    def add_bookmark(self):
        # Add current page as a bookmark (allow editing title)
        browser = self.tabs.currentWidget()
        if not isinstance(browser, QWebEngineView):
            QMessageBox.information(self, "Add Bookmark", "Current view is not a web page.")
            return
        url = browser.url().toString()
        title = browser.page().title() or url
        title, ok = QInputDialog.getText(self, "Add Bookmark", "Title:", text=title)
        if ok and title:
            # Ask whether to pin to toolbar
            resp = QMessageBox.question(self, "Pin to Toolbar", "Add this bookmark to the bookmarks toolbar?", QMessageBox.Yes | QMessageBox.No)
            pinned = True if resp == QMessageBox.Yes else False
            self.bookmarks.append({"title": title, "url": url, "pinned": pinned})
            self.save_bookmarks()
            self.refresh_bookmarks_toolbar()
            QMessageBox.information(self, "Bookmark Added", f"Added '{title}'")

    def view_bookmarks(self):
        # Show bookmarks in a dialog with open/delete
        dlg = QDialog(self)
        dlg.setWindowTitle("Bookmarks")
        dlg.resize(600, 400)
        layout = QVBoxLayout()

        listw = QListWidget()
        for bm in self.bookmarks:
            item = QListWidgetItem(bm.get("title", bm.get("url", "")))
            item.setData(Qt.UserRole, bm.get("url", ""))
            listw.addItem(item)

        layout.addWidget(listw)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open Selected", self)
        delete_btn = QPushButton("Delete Selected", self)
        close_btn = QPushButton("Close", self)

        def open_selected():
            sel = listw.currentItem()
            if sel:
                url = sel.data(Qt.UserRole)
                self.tabs.currentWidget().setUrl(QUrl(url))
                dlg.accept()

        def delete_selected():
            row = listw.currentRow()
            if row >= 0:
                confirm = QMessageBox.question(self, "Delete Bookmark", "Delete selected bookmark?", QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    listw.takeItem(row)
                    try:
                        self.bookmarks.pop(row)
                        self.save_bookmarks()
                        self.refresh_bookmarks_toolbar()
                    except Exception:
                        pass

        open_btn.clicked.connect(open_selected)
        delete_btn.clicked.connect(delete_selected)
        close_btn.clicked.connect(dlg.reject)

        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        dlg.setLayout(layout)
        listw.itemDoubleClicked.connect(lambda it: (self.tabs.currentWidget().setUrl(QUrl(it.data(Qt.UserRole))), dlg.accept()))
        dlg.exec_()
    def open_devtools(self):
        browser = self.tabs.currentWidget()
        if not isinstance(browser, QWebEngineView):
            return

        # Create devtools page using SAME profile
        devtools_page = QWebEnginePage(browser.page().profile())


        devtools_page.setInspectedPage(browser.page())

        browser.page().setDevToolsPage(devtools_page)
        self.devtools_view.setPage(devtools_page)

        # Toggle dock visibility (Chrome-like)
        if self.devtools_dock.isVisible():
            self.devtools_dock.hide()
        else:
            self.devtools_dock.show()
            self.devtools_dock.raise_()

    def toggle_bookmarks_toolbar(self, checked: bool):
        if checked:
            self.bookmarks_toolbar.show()
        else:
            self.bookmarks_toolbar.hide()
        # keep action state in sync
        try:
            self.toggle_bookmarks_toolbar_action.setChecked(self.bookmarks_toolbar.isVisible())
        except Exception:
            pass

app = QApplication(sys.argv)
QApplication.setApplicationName("HHBrowser")
window = SimpleBrowser()
window.show()  # Ensure the window is shown
app.exec_()
print("Application closed")
