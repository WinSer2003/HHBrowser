"""
Example Add-on: Custom Search Shortcuts
Adds quick search shortcuts for popular search engines
"""

from addon_system import HBrowserAddon


class SearchShortcutsAddon(HBrowserAddon):
    def __init__(self):
        super().__init__()
        self.name = "Search Shortcuts"
        self.version = "1.0.0"
        self.description = "Provides quick search shortcuts for popular search engines"
        self.author = "HHBrowser Team"
        
        self.search_engines = {
            "Google": "https://www.google.com/search?q=",
            "DuckDuckGo": "https://www.duckduckgo.com/?q=",
            "Bing": "https://www.bing.com/search?q=",
            "GitHub": "https://github.com/search?q=",
            "Wikipedia": "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=",
            "YouTube": "https://www.youtube.com/results?search_query=",
        }

    def init(self, browser_instance) -> bool:
        """Initialize the addon"""
        self.browser_instance = browser_instance
        print(f"✓ {self.name} initialized with {len(self.search_engines)} search engines")
        return True

    def unload(self) -> bool:
        """Clean up addon"""
        return True

    def get_menu_actions(self):
        """Provide menu actions for search shortcuts"""
        actions = []
        for engine_name in sorted(self.search_engines.keys()):
            actions.append({
                "menu": "Tools",
                "label": f"Search {engine_name}...",
                "callback": lambda e=engine_name: self._search(e)
            })
        return actions

    def _search(self, engine_name: str):
        """Perform a search on selected engine"""
        try:
            from PyQt5.QtWidgets import QInputDialog
            query, ok = QInputDialog.getText(
                self.browser_instance,
                f"Search {engine_name}",
                f"Enter search query for {engine_name}:"
            )
            
            if ok and query:
                search_url = self.search_engines[engine_name] + query.replace(" ", "+")
                browser = self.browser_instance.tabs.currentWidget()
                if browser:
                    from PyQt5.QtCore import QUrl
                    browser.setUrl(QUrl(search_url))
        except Exception as e:
            print(f"Error during search: {e}")
