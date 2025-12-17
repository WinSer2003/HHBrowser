"""
Add-on System for HHBrowser
Provides a plugin architecture for extending browser functionality
"""

import os
import sys
import json
import importlib.util
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable, Any
from enum import Enum


class AddonStatus(Enum):
    """Addon status enumeration"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"


class HBrowserAddon(ABC):
    """
    Base class for HHBrowser add-ons.
    All custom add-ons should inherit from this class.
    """

    def __init__(self):
        self.name: str = "Unnamed Add-on"
        self.version: str = "1.0.0"
        self.description: str = "No description"
        self.author: str = "Unknown"
        self.enabled: bool = False
        self.browser_instance = None

    @abstractmethod
    def init(self, browser_instance) -> bool:
        """
        Initialize the add-on.
        
        Args:
            browser_instance: Reference to the SimpleBrowser instance
            
        Returns:
            bool: True if initialization was successful
        """
        pass

    @abstractmethod
    def unload(self) -> bool:
        """
        Clean up and unload the add-on.
        
        Returns:
            bool: True if unload was successful
        """
        pass

    def on_tab_created(self, tab_index: int, browser_widget) -> None:
        """Called when a new tab is created"""
        pass

    def on_tab_closed(self, tab_index: int) -> None:
        """Called when a tab is closed"""
        pass

    def on_url_changed(self, url: str) -> None:
        """Called when URL changes"""
        pass

    def on_page_loaded(self, url: str, title: str) -> None:
        """Called when a page finishes loading"""
        pass

    def on_download_started(self, filename: str, path: str) -> None:
        """Called when a download starts"""
        pass

    def get_menu_actions(self) -> List[Dict[str, Any]]:
        """
        Return list of menu actions provided by this add-on.
        
        Returns:
            List of dicts with keys: 'menu' (str), 'label' (str), 'callback' (callable)
        """
        return []

    def get_context_menu_actions(self) -> List[Dict[str, Any]]:
        """Return list of context menu actions"""
        return []

    def get_toolbar_actions(self) -> List[Dict[str, Any]]:
        """Return list of toolbar actions"""
        return []

    def get_settings_ui(self):
        """
        Return a QWidget for addon settings, or None if no settings.
        This widget will be displayed in the addon settings dialog.
        """
        return None

    def save_settings(self, settings: Dict) -> None:
        """Called when addon settings need to be saved"""
        pass

    def load_settings(self, settings: Dict) -> None:
        """Called when addon settings are loaded from storage"""
        pass


class AddonManager:
    """Manages add-on loading, lifecycle, and hooks"""

    def __init__(self, addons_dir: str = "addons"):
        self.addons_dir = addons_dir
        self.addons: Dict[str, HBrowserAddon] = {}
        self.addon_configs: Dict[str, Dict] = {}
        self.browser_instance = None
        self.hooks: Dict[str, List[Callable]] = {
            'on_tab_created': [],
            'on_tab_closed': [],
            'on_url_changed': [],
            'on_page_loaded': [],
            'on_download_started': [],
        }
        self._ensure_addon_dir()
        self._load_addon_configs()

    def _ensure_addon_dir(self):
        """Ensure addon directory exists"""
        if not os.path.exists(self.addons_dir):
            os.makedirs(self.addons_dir)

    def _load_addon_configs(self):
        """Load addon configuration from addons.json"""
        config_file = os.path.join(self.addons_dir, "addons.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    self.addon_configs = json.load(f)
            except Exception as e:
                print(f"Error loading addon configs: {e}")

    def _read_manifest(self, addon_name: str) -> Dict:
        """Read manifest.json from addon folder and return dict (or empty dict)."""
        manifest_file = os.path.join(self.addons_dir, addon_name, "manifest.json")
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading manifest for {addon_name}: {e}")
        return {}

    def _save_addon_configs(self):
        """Save addon configuration to addons.json"""
        config_file = os.path.join(self.addons_dir, "addons.json")
        try:
            with open(config_file, "w") as f:
                json.dump(self.addon_configs, f, indent=2)
        except Exception as e:
            print(f"Error saving addon configs: {e}")

    def discover_addons(self) -> List[str]:
        """
        Discover available add-ons in the addons directory.
        
        Returns:
            List of addon module names
        """
        if not os.path.exists(self.addons_dir):
            return []

        addons = []
        for item in os.listdir(self.addons_dir):
            item_path = os.path.join(self.addons_dir, item)
            # Only consider folder-based addons that include a manifest.json
            if os.path.isdir(item_path):
                manifest = os.path.join(item_path, "manifest.json")
                if os.path.exists(manifest):
                    addons.append(item)

        return sorted(addons)

    def load_addon(self, addon_name: str) -> bool:
        """
        Load a single add-on by name.
        
        Args:
            addon_name: Name of the addon (module name without .py)
            
        Returns:
            bool: True if successfully loaded
        """
        if addon_name in self.addons:
            print(f"Add-on '{addon_name}' is already loaded")
            return False

        try:
            # Read manifest (if present) and determine entrypoint
            manifest = self._read_manifest(addon_name)
            main_entry = manifest.get("main") if isinstance(manifest, dict) else None

            addon_path = self._find_addon_file(addon_name, main_entry)
            if not addon_path:
                print(f"Add-on '{addon_name}' not found")
                return False

            # Load the module
            spec = importlib.util.spec_from_file_location(addon_name, addon_path)
            if not spec or not spec.loader:
                print(f"Cannot load spec for '{addon_name}'")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[addon_name] = module
            spec.loader.exec_module(module)

            # Find the addon class (should inherit from HBrowserAddon)
            addon_class = self._find_addon_class(module)
            if not addon_class:
                print(f"No HBrowserAddon subclass found in '{addon_name}'")
                return False

            # Instantiate and initialize
            addon_instance = addon_class()
            # Populate metadata from manifest if available
            try:
                if manifest:
                    addon_instance.name = manifest.get("name", addon_instance.name)
                    addon_instance.version = manifest.get("version", addon_instance.version)
                    addon_instance.description = manifest.get("description", addon_instance.description)
                    addon_instance.author = manifest.get("author", addon_instance.author)
            except Exception:
                pass
            if self.browser_instance and addon_instance.init(self.browser_instance):
                addon_instance.enabled = True
                self.addons[addon_name] = addon_instance
                
                # Register hooks
                self._register_addon_hooks(addon_name, addon_instance)
                
                # Store config
                # Ensure addon config exists (persist manifest defaults)
                if addon_name not in self.addon_configs:
                    self.addon_configs[addon_name] = {
                        "enabled": manifest.get("enabled", True) if isinstance(manifest, dict) else True,
                        "name": addon_instance.name,
                        "version": addon_instance.version,
                        "settings": manifest.get("settings", {}) if isinstance(manifest, dict) else {}
                    }
                    self._save_addon_configs()
                
                print(f"✓ Add-on '{addon_instance.name}' ({addon_name}) loaded successfully")
                return True
            else:
                print(f"Failed to initialize add-on '{addon_name}'")
                return False

        except Exception as e:
            print(f"Error loading add-on '{addon_name}': {e}")
            import traceback
            traceback.print_exc()
            return False

    def unload_addon(self, addon_name: str) -> bool:
        """
        Unload a single add-on.
        
        Args:
            addon_name: Name of the addon
            
        Returns:
            bool: True if successfully unloaded
        """
        if addon_name not in self.addons:
            return False

        try:
            addon = self.addons[addon_name]
            if addon.unload():
                del self.addons[addon_name]
                # Remove from hooks
                for hook_list in self.hooks.values():
                    hook_list[:] = [h for h in hook_list if h.__self__ != addon]
                
                if addon_name in self.addon_configs:
                    self.addon_configs[addon_name]["enabled"] = False
                
                print(f"✓ Add-on '{addon_name}' unloaded")
                return True
        except Exception as e:
            print(f"Error unloading add-on '{addon_name}': {e}")

        return False

    def load_all_addons(self, browser_instance) -> Dict[str, bool]:
        """
        Discover and load all available add-ons.
        
        Args:
            browser_instance: Reference to SimpleBrowser instance
            
        Returns:
            Dict with addon names and their load status
        """
        self.browser_instance = browser_instance
        results = {}
        
        for addon_name in self.discover_addons():
            # Load manifest to seed addon_configs with defaults
            manifest = self._read_manifest(addon_name)
            if addon_name not in self.addon_configs and manifest:
                self.addon_configs[addon_name] = {
                    "enabled": manifest.get("enabled", True),
                    "name": manifest.get("name", addon_name),
                    "version": manifest.get("version", "Unknown"),
                    "settings": manifest.get("settings", {}),
                }

            # Check if addon should be enabled
            addon_config = self.addon_configs.get(addon_name, {})
            should_load = addon_config.get("enabled", True)

            if should_load:
                results[addon_name] = self.load_addon(addon_name)
            else:
                results[addon_name] = False

        return results

    def _find_addon_file(self, addon_name: str, main_entry: str = None) -> Optional[str]:
        """Find the file path for an addon. If main_entry provided, try that first."""
        # Backwards compatibility: allow single-file addons
        py_file = os.path.join(self.addons_dir, f"{addon_name}.py")
        if os.path.exists(py_file):
            return py_file

        # If the addon is a folder, check for provided main entry or __init__.py
        folder = os.path.join(self.addons_dir, addon_name)
        if os.path.isdir(folder):
            # If main entry specified, try that
            main_entry_path = None
            if main_entry:
                main_entry_path = os.path.join(folder, main_entry)
                if os.path.exists(main_entry_path):
                    return main_entry_path

            # attempt to read manifest main entry as fallback
            manifest_file = os.path.join(folder, "manifest.json")
            if os.path.exists(manifest_file):
                try:
                    with open(manifest_file, "r") as f:
                        m = json.load(f)
                        m_main = m.get("main")
                        if m_main:
                            m_main_path = os.path.join(folder, m_main)
                            if os.path.exists(m_main_path):
                                return m_main_path
                except Exception:
                    pass

            # Fallback to __init__.py or main.py
            init_file = os.path.join(folder, "__init__.py")
            if os.path.exists(init_file):
                return init_file
            main_py = os.path.join(folder, "main.py")
            if os.path.exists(main_py):
                return main_py

        return None

    def _find_addon_class(self, module):
        """Find HBrowserAddon subclass in module"""
        for item_name in dir(module):
            item = getattr(module, item_name)
            if (
                isinstance(item, type)
                and issubclass(item, HBrowserAddon)
                and item is not HBrowserAddon
            ):
                return item
        return None

    def _register_addon_hooks(self, addon_name: str, addon: HBrowserAddon):
        """Register addon hooks"""
        # Register lifecycle hooks
        if hasattr(addon, 'on_tab_created'):
            self.hooks['on_tab_created'].append(addon.on_tab_created)
        if hasattr(addon, 'on_tab_closed'):
            self.hooks['on_tab_closed'].append(addon.on_tab_closed)
        if hasattr(addon, 'on_url_changed'):
            self.hooks['on_url_changed'].append(addon.on_url_changed)
        if hasattr(addon, 'on_page_loaded'):
            self.hooks['on_page_loaded'].append(addon.on_page_loaded)
        if hasattr(addon, 'on_download_started'):
            self.hooks['on_download_started'].append(addon.on_download_started)

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Trigger a specific hook"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in hook callback: {e}")

    def get_addon(self, addon_name: str) -> Optional[HBrowserAddon]:
        """Get a loaded addon by name"""
        return self.addons.get(addon_name)

    def get_all_addons(self) -> Dict[str, HBrowserAddon]:
        """Get all loaded addons"""
        return self.addons.copy()

    def get_addon_status(self, addon_name: str) -> Dict[str, Any]:
        """Get detailed status of an addon"""
        if addon_name not in self.addon_configs:
            return {}

        config = self.addon_configs[addon_name]
        is_loaded = addon_name in self.addons
        addon_obj = self.addons.get(addon_name)

        return {
            "name": config.get("name", addon_name),
            "version": config.get("version", "Unknown"),
            "enabled": config.get("enabled", False),
            "loaded": is_loaded,
            "status": AddonStatus.ENABLED if is_loaded else AddonStatus.DISABLED,
        }

    def set_addon_enabled(self, addon_name: str, enabled: bool) -> bool:
        """Enable or disable an addon"""
        if addon_name not in self.addon_configs:
            return False

        if enabled and addon_name not in self.addons:
            result = self.load_addon(addon_name)
        elif not enabled and addon_name in self.addons:
            result = self.unload_addon(addon_name)
        else:
            result = True

        if result:
            self.addon_configs[addon_name]["enabled"] = enabled
            self._save_addon_configs()

        return result
