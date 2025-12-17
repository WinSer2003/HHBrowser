"""
Example Add-on: Session Logger
Logs browser session events (tabs, navigation, downloads) to a file
"""

from addon_system import HBrowserAddon
from datetime import datetime
import os


class SessionLoggerAddon(HBrowserAddon):
    def __init__(self):
        super().__init__()
        self.name = "Session Logger"
        self.version = "1.0.0"
        self.description = "Logs browser session events to a file"
        self.author = "HHBrowser Team"
        self.log_file = os.path.join(os.path.dirname(__file__), "session_log.txt")

    def init(self, browser_instance) -> bool:
        """Initialize the addon"""
        self.browser_instance = browser_instance
        self._log("SESSION STARTED")
        return True

    def unload(self) -> bool:
        """Clean up addon"""
        self._log("SESSION ENDED")
        return True

    def on_tab_created(self, tab_index: int, browser_widget) -> None:
        """Called when a new tab is created"""
        self._log(f"New tab created: Tab #{tab_index + 1}")

    def on_tab_closed(self, tab_index: int) -> None:
        """Called when a tab is closed"""
        self._log(f"Tab closed: Tab #{tab_index + 1}")

    def on_url_changed(self, url: str) -> None:
        """Called when URL changes"""
        if url and not url.startswith("about:"):
            self._log(f"URL changed: {url}")

    def on_page_loaded(self, url: str, title: str) -> None:
        """Called when page finishes loading"""
        self._log(f"Page loaded: {title} ({url})")

    def on_download_started(self, filename: str, path: str) -> None:
        """Called when download starts"""
        self._log(f"Download started: {filename} -> {path}")

    def _log(self, message: str):
        """Write message to log file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            with open(self.log_file, "a") as f:
                f.write(log_message)
        except Exception as e:
            print(f"Error writing to session log: {e}")
