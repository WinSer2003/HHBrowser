"""
Example Add-on: Page Information Display
Shows page information (URL, title, load time) when pages finish loading
"""

from addon_system import HBrowserAddon
import time


class PageInfoAddon(HBrowserAddon):
    def __init__(self):
        super().__init__()
        self.name = "Page Info Display"
        self.version = "1.0.0"
        self.description = "Displays information about loaded pages"
        self.author = "HHBrowser Team"
        self.page_load_times = {}

    def init(self, browser_instance) -> bool:
        """Initialize the addon"""
        self.browser_instance = browser_instance
        print(f"✓ {self.name} initialized")
        return True

    def unload(self) -> bool:
        """Clean up addon"""
        print(f"✓ {self.name} unloaded")
        return True

    def on_url_changed(self, url: str) -> None:
        """Track when URL changes"""
        # Store the start time for this page load
        self.page_load_times[url] = time.time()

    def on_page_loaded(self, url: str, title: str) -> None:
        """Called when page finishes loading"""
        load_time = time.time() - self.page_load_times.get(url, time.time())
        
        # Print page info to console
        info = f"""
╔════════════════════════════════════════╗
║  Page Information                      ║
╠════════════════════════════════════════╣
║  Title:     {title[:30]:30}║
║  URL:       {url[:30]:30}║
║  Load Time: {load_time:.2f}s                    ║
╚════════════════════════════════════════╝
"""
        print(info)

    def get_menu_actions(self):
        """Provide menu actions"""
        return [
            {
                "menu": "Tools",
                "label": "Show Current Page Stats",
                "callback": self.show_page_stats
            }
        ]

    def show_page_stats(self):
        """Show statistics for current page"""
        try:
            browser = self.browser_instance.tabs.currentWidget()
            url = browser.url().toString()
            title = browser.page().title()
            print(f"Current Page: {title}\nURL: {url}")
        except Exception as e:
            print(f"Error: {e}")
