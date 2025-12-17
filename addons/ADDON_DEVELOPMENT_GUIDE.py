"""
Add-on Development Guide and Template

This file serves as a guide for developing custom add-ons for HHBrowser.
Copy this template and modify it to create your own add-on.
"""

from addon_system import HBrowserAddon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton


class MyCustomAddon(HBrowserAddon):
    """
    Template for creating custom add-ons.
    Replace 'MyCustomAddon' with your addon class name.
    """

    def __init__(self):
        super().__init__()
        # Basic metadata
        self.name = "My Custom Add-on"  # User-friendly name
        self.version = "1.0.0"  # Semantic versioning
        self.description = "Description of what your add-on does"
        self.author = "Your Name"
        
        # Store reference to browser (set during init)
        self.browser_instance = None

    def init(self, browser_instance) -> bool:
        """
        Initialize the add-on.
        Called when the add-on is loaded.
        
        Args:
            browser_instance: Reference to SimpleBrowser instance
            
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        self.browser_instance = browser_instance
        print(f"✓ {self.name} initialized successfully")
        # Perform any initialization here
        return True

    def unload(self) -> bool:
        """
        Clean up and unload the add-on.
        Called when the add-on is disabled.
        
        Returns:
            bool: True if unload succeeded, False otherwise
        """
        # Perform cleanup here
        print(f"✓ {self.name} unloaded")
        return True

    # ===== Optional Hook Methods =====
    # Uncomment the hooks you want to use

    def on_tab_created(self, tab_index: int, browser_widget) -> None:
        """Called when a new tab is created"""
        # print(f"Tab created at index {tab_index}")
        pass

    def on_tab_closed(self, tab_index: int) -> None:
        """Called when a tab is closed"""
        # print(f"Tab closed at index {tab_index}")
        pass

    def on_url_changed(self, url: str) -> None:
        """Called when URL changes in current tab"""
        # print(f"URL changed to: {url}")
        pass

    def on_page_loaded(self, url: str, title: str) -> None:
        """Called when a page finishes loading"""
        # print(f"Page loaded: {title}")
        pass

    def on_download_started(self, filename: str, path: str) -> None:
        """Called when a download starts"""
        # print(f"Download started: {filename}")
        pass

    # ===== Optional Menu/UI Methods =====

    def get_menu_actions(self):
        """
        Return list of menu actions provided by this add-on.
        
        Returns:
            List of dicts with keys: 'menu' (str), 'label' (str), 'callback' (callable)
            
        Example:
            return [
                {
                    "menu": "Tools",
                    "label": "My Action",
                    "callback": self.my_action_handler
                }
            ]
        """
        return []

    def get_toolbar_actions(self):
        """Return list of toolbar actions"""
        return []

    def get_context_menu_actions(self):
        """Return list of context menu actions"""
        return []

    def get_settings_ui(self):
        """
        Return a QWidget for addon settings.
        
        Returns:
            QWidget instance for settings UI, or None if no settings
        """
        return None

    def save_settings(self, settings: dict) -> None:
        """Called when addon settings need to be saved"""
        pass

    def load_settings(self, settings: dict) -> None:
        """Called when addon settings are loaded"""
        pass


# ===== QUICK START GUIDE =====
"""
1. Save this file as 'my_addon.py' in the addons/ directory

2. Edit the MyCustomAddon class:
   - Change the class name to something meaningful
   - Update name, version, description, author metadata
   
3. Implement the init() and unload() methods

4. Add any hook methods you need:
   - on_tab_created: Called when new tab opens
   - on_tab_closed: Called when tab closes
   - on_url_changed: Called when URL changes
   - on_page_loaded: Called when page finishes loading
   - on_download_started: Called when download begins

5. Optionally add menu actions via get_menu_actions()

6. Reload add-ons in HHBrowser (Tools > Add-ons > Reload Add-ons)

7. Enable your add-on in the Add-ons Manager (Tools > Add-ons > Manage Add-ons)

===== EXAMPLE: Simple Click Counter =====

from addon_system import HBrowserAddon

class ClickCounterAddon(HBrowserAddon):
    def __init__(self):
        super().__init__()
        self.name = "Click Counter"
        self.version = "1.0.0"
        self.description = "Counts page loads"
        self.author = "Developer"
        self.click_count = 0
    
    def init(self, browser_instance) -> bool:
        self.browser_instance = browser_instance
        return True
    
    def unload(self) -> bool:
        return True
    
    def on_page_loaded(self, url: str, title: str) -> None:
        self.click_count += 1
        print(f"Pages loaded: {self.click_count}")
    
    def get_menu_actions(self):
        return [{
            "menu": "Tools",
            "label": "Show Page Count",
            "callback": lambda: print(f"Total pages loaded: {self.click_count}")
        }]
"""
