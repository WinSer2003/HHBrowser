"""
My Custom Addon

Description of what your addon does and any usage notes.
"""

from addon_system import HBrowserAddon


class MyCustomAddon(HBrowserAddon):
    """
    Main addon class - inherits from HBrowserAddon.
    
    This is a template - customize the docstring, class name,
    and implement the hooks you need.
    """

    def __init__(self):
        super().__init__()
        # These will be overridden by manifest.json values
        self.name = "My Custom Addon"
        self.version = "1.0.0"
        self.description = "Description of what your addon does"
        self.author = "Your Name"

    def init(self, browser_instance) -> bool:
        """
        Initialize the addon.
        
        Called when the addon is loaded.
        Store the browser reference here for later use.
        
        Args:
            browser_instance: Reference to SimpleBrowser instance
            
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        self.browser_instance = browser_instance
        print(f"✓ {self.name} initialized")
        return True

    def unload(self) -> bool:
        """
        Clean up and unload the addon.
        
        Called when the addon is disabled.
        Clean up any resources here.
        
        Returns:
            bool: True if unload succeeded, False otherwise
        """
        print(f"✓ {self.name} unloaded")
        return True

    # ===== Optional Event Hooks =====
    # Uncomment the ones you want to use

    # def on_tab_created(self, tab_index: int, browser_widget) -> None:
    #     """Called when a new tab is created"""
    #     print(f"Tab created at index {tab_index}")

    # def on_tab_closed(self, tab_index: int) -> None:
    #     """Called when a tab is closed"""
    #     print(f"Tab closed at index {tab_index}")

    # def on_url_changed(self, url: str) -> None:
    #     """Called when URL changes in current tab"""
    #     print(f"URL changed to: {url}")

    # def on_page_loaded(self, url: str, title: str) -> None:
    #     """Called when a page finishes loading"""
    #     print(f"Page loaded: {title}")

    # def on_download_started(self, filename: str, path: str) -> None:
    #     """Called when a download starts"""
    #     print(f"Download started: {filename}")

    # ===== Optional UI Methods =====
    # Uncomment the ones you want to use

    # def get_menu_actions(self):
    #     """Return list of menu actions provided by this addon"""
    #     return [{
    #         "menu": "Tools",
    #         "label": "My Action",
    #         "callback": self.my_action_handler
    #     }]

    # def my_action_handler(self):
    #     """Handle menu action"""
    #     print("Menu action clicked!")

    # def get_toolbar_actions(self):
    #     """Return list of toolbar actions"""
    #     return []

    # def get_context_menu_actions(self):
    #     """Return list of context menu actions"""
    #     return []

    # def get_settings_ui(self):
    #     """Return QWidget for addon settings"""
    #     return None

    # def save_settings(self, settings: dict) -> None:
    #     """Called when addon settings need to be saved"""
    #     pass

    # def load_settings(self, settings: dict) -> None:
    #     """Called when addon settings are loaded"""
    #     pass


# ===== EXAMPLES =====

# Example 1: Simple Hook Usage
# def on_page_loaded(self, url: str, title: str) -> None:
#     print(f"✓ Page loaded: {title}")

# Example 2: Accessing Browser Data
# def on_page_loaded(self, url: str, title: str) -> None:
#     current_tab = self.browser_instance.tabs.currentWidget()
#     url = current_tab.url().toString()
#     print(f"URL: {url}")

# Example 3: Adding Menu Actions
# def get_menu_actions(self):
#     return [{
#         "menu": "Tools",
#         "label": "My Custom Action",
#         "callback": self.handle_action
#     }]
#
# def handle_action(self):
#     print("Action executed!")

# Example 4: Storing Data
# import os, json
# def save_data(self):
#     addon_dir = os.path.dirname(__file__)
#     data_file = os.path.join(addon_dir, "data.json")
#     with open(data_file, "w") as f:
#         json.dump({"key": "value"}, f)
