# HHBrowser Add-on System

A powerful and flexible plugin architecture for extending HHBrowser with custom functionalities. Add-ons are self-contained packages with their own configuration, code, and resources.

## Overview

The Add-on System allows developers to create custom extensions for HHBrowser without modifying the core application. Add-ons can:

- Monitor browser events (tab creation, navigation, page loads, downloads)
- Add custom menu items and toolbar actions
- Log and analyze browser activity
- Integrate custom search engines
- Store data and configuration locally
- Extend browser functionality in unlimited ways

## Key Features

✅ **Plugin Discovery**: Automatically discovers add-ons in the `addons/` directory  
✅ **Manifest-Based**: Each add-on has a `manifest.json` with metadata  
✅ **Lifecycle Management**: Load, enable, disable, and unload add-ons dynamically  
✅ **Event Hooks**: Subscribe to important browser events  
✅ **Settings Persistence**: Auto-save enabled/disabled state and user settings  
✅ **Hot Reload**: Reload all add-ons without restarting the browser  
✅ **Easy Installation**: Drop in add-on folders and reload  

### Available Hooks
- `on_tab_created`: Triggered when a new tab is created
- `on_tab_closed`: Triggered when a tab is closed
- `on_url_changed`: Triggered when URL changes
- `on_page_loaded`: Triggered when page finishes loading
- `on_download_started`: Triggered when a download begins

## Quick Start

### For Users: Managing Add-ons

1. **Open Add-ons Manager**: `Tools > Add-ons > Manage Add-ons`
2. **View Available Add-ons**: All add-ons in the `addons/` folder appear in the list
3. **Enable/Disable**: Select an add-on and click "Enable Selected" or "Disable Selected"
4. **View Info**: Click "Info" to see version, description, and author
5. **Access Features**: Check the `Tools` menu for add-on actions

### For Developers: Creating Your First Add-on

#### Step 1: Create the Folder Structure

```bash
mkdir -p addons/my_addon
```

#### Step 2: Create `manifest.json`

Create `addons/my_addon/manifest.json`:

```json
{
  "name": "My Custom Add-on",
  "version": "1.0.0",
  "description": "What your add-on does",
  "author": "Your Name",
  "main": "addon.py",
  "enabled": true,
  "license": "MIT"
}
```

#### Step 3: Create `addon.py`

Create `addons/my_addon/addon.py`:

```python
from addon_system import HBrowserAddon

class MyAddon(HBrowserAddon):
    def init(self, browser_instance) -> bool:
        print("✓ My addon loaded!")
        self.browser_instance = browser_instance
        return True
    
    def unload(self) -> bool:
        print("✓ My addon unloaded")
        return True
```

#### Step 4: Reload Add-ons

In HHBrowser: `Tools > Add-ons > Reload Add-ons`

#### Step 5: Enable Your Add-on

1. Open `Tools > Add-ons > Manage Add-ons`
2. Select your add-on
3. Click "Enable Selected"

✅ Your add-on is now active!

#### Step 6: Add Event Hooks (Optional)

```python
def on_page_loaded(self, url: str, title: str) -> None:
    print(f"Page loaded: {title}")

def on_url_changed(self, url: str) -> None:
    print(f"URL changed: {url}")
```

## Structure

**Important**: Add-ons MUST be in **folders** with a **manifest.json** file to be discovered.

```
addons/
├── addons.json                          # Generated: tracks enabled/disabled state
├── page_info/                           # Example: Page Info Display addon
│   ├── manifest.json                   # Addon metadata
│   └── addon.py                        # Addon code
├── session_logger/                      # Example: Session Logger addon
│   ├── manifest.json
│   ├── addon.py
│   └── session_log.txt                 # Generated: session logs
├── search_shortcuts/                    # Example: Search Shortcuts addon
│   ├── manifest.json
│   └── addon.py
├── my_addon/                            # Your custom addon
│   ├── manifest.json                   # REQUIRED
│   ├── addon.py                        # REQUIRED
│   └── resources/                      # Optional: icons, configs, data
└── README.md                            # This file
```

### Key Requirements

For an add-on to be discovered and loaded:

1. ✅ Addon must be in a **folder** (not a loose .py file)
2. ✅ Folder must contain `manifest.json`
3. ✅ `manifest.json` must have these fields:
   - `name`: Display name
   - `version`: Semantic version (1.0.0)
   - `description`: What it does
   - `author`: Author name
   - `main`: Entry point file (e.g., "addon.py")
4. ✅ Main file must have a class inheriting from `HBrowserAddon`
5. ✅ Class must implement `init()` and `unload()` methods

## Example Add-ons Included

### 1. Page Info Display (`page_info/`)
- Shows page title, URL, and load time when pages finish loading
- Demonstrates the `on_page_loaded` hook
- Provides a menu action to show current page stats
- **Status**: Enabled by default

### 2. Session Logger (`session_logger/`)
- Logs all browser events to `addons/session_logger/session_log.txt`
- Demonstrates all lifecycle hooks
- Useful for monitoring and debugging browser activity
- **Status**: Enabled by default

### 3. Search Shortcuts (`search_shortcuts/`)
- Adds quick search options for 6 popular search engines (Google, DuckDuckGo, Bing, GitHub, Wikipedia, YouTube)
- Demonstrates menu action integration
- Shows how to interact with browser tabs
- **Status**: Enabled by default

## Creating Your First Add-on

### Complete Example: Page Statistics Add-on

#### Directory Structure

```
addons/page_stats/
├── manifest.json
├── addon.py
└── README.md
```

#### 1. manifest.json

```json
{
  "name": "Page Statistics",
  "version": "1.0.0",
  "description": "Track and display page loading statistics",
  "author": "Your Name",
  "main": "addon.py",
  "enabled": true,
  "license": "MIT",
  "keywords": ["stats", "monitoring", "pages"]
}
```

#### 2. addon.py

```python
from addon_system import HBrowserAddon
import time
from datetime import datetime

class PageStatsAddon(HBrowserAddon):
    def __init__(self):
        super().__init__()
        self.name = "Page Statistics"
        self.version = "1.0.0"
        self.description = "Track and display page loading statistics"
        self.author = "Your Name"
        self.page_loads = []
        self.load_times = {}

    def init(self, browser_instance) -> bool:
        self.browser_instance = browser_instance
        print(f"✓ {self.name} initialized")
        return True

    def unload(self) -> bool:
        print(f"✓ {self.name} unloaded")
        return True

    def on_url_changed(self, url: str) -> None:
        """Track when a new page starts loading"""
        self.load_times[url] = time.time()

    def on_page_loaded(self, url: str, title: str) -> None:
        """Track when a page finishes loading"""
        load_time = time.time() - self.load_times.get(url, time.time())
        self.page_loads.append({
            "url": url,
            "title": title,
            "time": load_time,
            "timestamp": datetime.now().isoformat()
        })
        print(f"Page loaded in {load_time:.2f}s: {title}")

    def get_menu_actions(self):
        return [{
            "menu": "Tools",
            "label": "Show Page Statistics",
            "callback": self.show_stats
        }]

    def show_stats(self):
        """Display statistics about loaded pages"""
        if not self.page_loads:
            print("No pages loaded yet")
            return
        
        avg_time = sum(p["time"] for p in self.page_loads) / len(self.page_loads)
        max_time = max(p["time"] for p in self.page_loads)
        min_time = min(p["time"] for p in self.page_loads)
        
        print(f"""
╔════════════════════════════════╗
║  Page Load Statistics          ║
╠════════════════════════════════╣
║  Total Pages:      {len(self.page_loads):19} ║
║  Avg Load Time:    {avg_time:18.2f}s ║
║  Max Load Time:    {max_time:18.2f}s ║
║  Min Load Time:    {min_time:18.2f}s ║
╚════════════════════════════════╝
""")
```

#### 3. Test Your Add-on

1. Reload: `Tools > Add-ons > Reload Add-ons`
2. Enable: `Tools > Add-ons > Manage Add-ons` → Enable "Page Statistics"
3. Use: Go to `Tools > Show Page Statistics` after loading some pages

## Creating Your First Add-on

### Step 1: Create the Add-on Folder Structure

```bash
mkdir -p addons/hello_world
```

### Step 2: Create the Manifest File

Create `addons/hello_world/manifest.json`:

```json
{
  "name": "Hello World",
  "version": "1.0.0",
  "description": "A simple hello world add-on",
  "author": "Your Name",
  "main": "addon.py",
  "enabled": true
}
```

### Step 3: Create the Add-on Code

Create `addons/hello_world/addon.py`:

```python
from addon_system import HBrowserAddon

class HelloWorldAddon(HBrowserAddon):
    def init(self, browser_instance) -> bool:
        print("✓ Hello World Add-on loaded!")
        self.browser_instance = browser_instance
        return True
    
    def unload(self) -> bool:
        print("✓ Hello World Add-on unloaded")
        return True
    
    def on_page_loaded(self, url: str, title: str) -> None:
        print(f"Loaded: {title}")
```

### Step 4: Reload Add-ons

In HHBrowser: `Tools > Add-ons > Reload Add-ons`

### Step 5: Enable the Add-on

1. Open `Tools > Add-ons > Manage Add-ons`
2. Select "Hello World"
3. Click "Enable Selected"

### Step 6: Test

Open a webpage and watch the console for "Loaded: [page title]"

## API Reference

### Manifest.json Format

Every add-on **must** have a `manifest.json` file in its root folder:

```json
{
  "name": "Add-on Display Name",
  "version": "1.0.0",
  "description": "Short description of what the add-on does",
  "author": "Author Name",
  "main": "addon.py",
  "enabled": true,
  "license": "MIT",
  "keywords": ["browser", "example"],
  "settings": {}
}
```

**Required Fields:**
- `name` (string): Display name of the add-on
- `version` (string): Semantic version (e.g., 1.0.0)
- `description` (string): What the add-on does
- `author` (string): Author name
- `main` (string): Entry point Python file (usually `addon.py`)

**Optional Fields:**
- `enabled` (boolean): Default enabled state (default: true)
- `license` (string): License type (MIT, GPL, etc.)
- `keywords` (array): Search keywords
- `settings` (object): Default add-on settings

### Manifest.json Examples

#### Minimal Manifest

```json
{
  "name": "Simple Add-on",
  "version": "1.0.0",
  "description": "A minimal add-on",
  "author": "Your Name",
  "main": "addon.py"
}
```

#### Full-Featured Manifest

```json
{
  "name": "Advanced Add-on",
  "version": "2.1.0",
  "description": "A comprehensive add-on with all features",
  "author": "Your Name",
  "main": "addon.py",
  "license": "MIT",
  "keywords": ["browser", "monitoring", "analytics"],
  "enabled": true,
  "settings": {
    "log_level": "info",
    "auto_backup": true,
    "backup_interval": 3600
  }
}
```

#### Page Info Display Example

```json
{
  "name": "Page Info Display",
  "version": "1.0.0",
  "description": "Shows page information (URL, title, load time) when pages finish loading",
  "author": "HHBrowser Team",
  "main": "addon.py",
  "license": "MIT",
  "keywords": ["page", "info", "stats", "monitoring"],
  "enabled": true
}
```

### HBrowserAddon Base Class

All add-ons must inherit from `HBrowserAddon`.

#### Required Methods

```python
def init(self, browser_instance) -> bool:
    """Initialize the add-on. Return True if successful."""
    pass

def unload(self) -> bool:
    """Clean up the add-on. Return True if successful."""
    pass
```

#### Optional Lifecycle Hooks

```python
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
```

#### Optional UI Methods

```python
def get_menu_actions(self) -> List[Dict]:
    """Return menu actions"""
    return [{
        "menu": "Tools",  # Menu name
        "label": "Action Label",  # Action label
        "callback": self.action_handler  # Callable
    }]

def get_toolbar_actions(self) -> List[Dict]:
    """Return toolbar actions"""
    pass

def get_context_menu_actions(self) -> List[Dict]:
    """Return context menu actions"""
    pass

def get_settings_ui(self):
    """Return QWidget for settings, or None"""
    pass

def save_settings(self, settings: dict) -> None:
    """Save add-on settings"""
    pass

def load_settings(self, settings: dict) -> None:
    """Load add-on settings"""
    pass
```

## Add-on Configuration (addons.json)

Auto-generated and managed by HHBrowser. Stores enabled/disabled state and user settings:

```json
{
  "example_page_info": {
    "enabled": true,
    "name": "Page Info Display",
    "version": "1.0.0",
    "settings": {}
  },
  "example_session_logger": {
    "enabled": false,
    "name": "Session Logger",
    "version": "1.0.0",
    "settings": {}
  }
}
```

Metadata (name, version, description) is read from each addon's `manifest.json`, so you never need to edit this file manually.

## Best Practices

1. **Use Meaningful Names**: Make your add-on name descriptive
2. **Handle Errors**: Wrap code in try-except blocks
3. **Don't Block**: Keep hooks fast to avoid freezing the browser
4. **Clean Up**: Always implement proper cleanup in `unload()`
5. **Follow Conventions**: Use semantic versioning (1.0.0, 2.1.3, etc.)
6. **Documentation**: Include docstrings and comments
7. **Testing**: Test your add-on thoroughly before releasing

## Troubleshooting

### ❌ Add-on Not Appearing in Manager

**Problem**: You created a folder but it doesn't show up in `Tools > Add-ons > Manage Add-ons`

**Solutions**:
1. **Check Manifest**: Verify that `manifest.json` exists in your addon folder
   ```bash
   ls addons/my_addon/manifest.json  # Should exist
   ```

2. **Validate JSON**: Make sure the manifest JSON is valid
   ```bash
   python -m json.tool addons/my_addon/manifest.json  # Should not error
   ```

3. **Check Required Fields**: Your manifest must have these fields:
   ```json
   {
     "name": "Add-on Name",
     "version": "1.0.0",
     "description": "What it does",
     "author": "Your Name",
     "main": "addon.py"
   }
   ```

4. **Reload Add-ons**: After fixing, reload in HHBrowser: `Tools > Add-ons > Reload Add-ons`

### ❌ Add-on Shows But Won't Enable

**Problem**: Add-on appears in the manager but clicking "Enable Selected" doesn't work

**Solutions**:
1. **Check Console**: Look for error messages in the console output
2. **Verify Main File**: Check that the file specified in `"main"` exists:
   ```bash
   ls addons/my_addon/addon.py  # Should exist if "main": "addon.py"
   ```

3. **Check Class**: The Python file must contain a class inheriting from `HBrowserAddon`:
   ```python
   from addon_system import HBrowserAddon
   class MyAddon(HBrowserAddon):
       ...
   ```

4. **Check Methods**: The class must implement `init()` and `unload()` methods that return `bool`

### ❌ Add-on Loads but Doesn't Work

**Problem**: Add-on appears enabled but features don't work

**Solutions**:
1. **Check Console**: Print debug statements to console
   ```python
   print("Debug: Hook called!")
   ```

2. **Verify Hooks**: Make sure hook methods have correct signatures:
   ```python
   def on_page_loaded(self, url: str, title: str) -> None:
       print(f"Page: {title}")
   ```

3. **Test init()**: Check that `init()` returns `True`:
   ```python
   def init(self, browser_instance) -> bool:
       self.browser_instance = browser_instance
       return True  # MUST return True
   ```

4. **Reload to Test**: Changes to addon.py require a reload: `Tools > Add-ons > Reload Add-ons`

### ⚠️ Common Mistakes

| Mistake | Solution |
|---------|----------|
| `"main": "__init__.py"` | Change to `"main": "addon.py"` (no __init__.py needed) |
| No `manifest.json` | Create it in addon folder |
| Missing import | Add `from addon_system import HBrowserAddon` |
| `init()` returns `None` | Make sure to `return True` |
| Manifest syntax error | Use `python -m json.tool` to validate |
| Addon folder missing | Create with `mkdir addons/my_addon` |
| Addon in root addons.py | Move to folder with manifest.json |

### ℹ️ How Add-ons Are Discovered

1. HHBrowser looks in the `addons/` directory
2. Only **folders** are considered (not loose .py files)
3. Each folder **must** contain `manifest.json`
4. The `manifest.json` **must** be valid JSON
5. The `manifest.json` **must** have required fields
6. The file specified in `"main"` must exist in the folder
7. The main file must contain a class inheriting from `HBrowserAddon`

### ℹ️ How Add-on State is Managed

- **addons.json**: Stores enabled/disabled state and user settings
- **manifest.json**: Contains add-on metadata (name, version, description)
- Both are used together:
  - manifest.json provides the info to display
  - addons.json tracks which are enabled
  - New add-ons automatically added to addons.json on first load

## Advanced Features

### Project Structure for Complex Add-ons

For larger add-ons, you can organize code into multiple files:

```
addons/my_complex_addon/
├── manifest.json          # Metadata
├── addon.py               # Main entry point (defines addon class)
├── utils.py               # Utility functions
├── handlers.py            # Event handlers
├── resources/
│   ├── icons/
│   ├── config.json
│   └── data.json
└── README.md              # Addon documentation
```

### Accessing Browser Methods

```python
# Get current tab
current_tab = self.browser_instance.tabs.currentWidget()

# Get URL
url = current_tab.url().toString()

# Get page title
title = current_tab.page().title()

# Navigate to URL
from PyQt5.QtCore import QUrl
current_tab.setUrl(QUrl("https://example.com"))
```

### Storing Add-on Data

```python
import json
import os

class MyAddon(HBrowserAddon):
    def get_addon_dir(self):
        """Get the addon's folder path"""
        # Addon folder is where addon.py is located
        return os.path.dirname(os.path.abspath(__file__))
    
    def save_data(self, data):
        """Save data to addon folder"""
        addon_dir = self.get_addon_dir()
        data_file = os.path.join(addon_dir, "data.json")
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load data from addon folder"""
        addon_dir = self.get_addon_dir()
        data_file = os.path.join(addon_dir, "data.json")
        if os.path.exists(data_file):
            with open(data_file) as f:
                return json.load(f)
        return {}
```

### Using Add-on Resources

Each addon can include static resources (icons, configs, etc.):

```python
import os
import json

class MyAddon(HBrowserAddon):
    def init(self, browser_instance) -> bool:
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load configuration
        config_path = os.path.join(self.addon_dir, "resources", "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        
        self.browser_instance = browser_instance
        return True
```

## Support

For issues, questions, or feature requests, please refer to the HHBrowser documentation or create an issue on the project repository.

## Quick Checklist: Creating a New Add-on

Use this checklist when creating a new add-on:

- [ ] Create addon folder: `addons/my_addon/`
- [ ] Create `manifest.json` with all required fields
- [ ] Create `addon.py` with your addon class
- [ ] Class name something meaningful (e.g., `MyAddon`)
- [ ] Class inherits from `HBrowserAddon`
- [ ] Implement `init(browser_instance) -> bool` returning True
- [ ] Implement `unload() -> bool` returning True
- [ ] Test by reloading: `Tools > Add-ons > Reload Add-ons`
- [ ] Enable addon: `Tools > Add-ons > Manage Add-ons`
- [ ] Verify it works
- [ ] Add hooks for events you want to monitor
- [ ] Test thoroughly
- [ ] Document features in README or comments
- [ ] Include license information in manifest.json

## Need Help?

### Check These Example Add-ons

1. **Simple**: Start with `page_info/` - minimal addon with one hook
2. **Complete**: Study `session_logger/` - uses all event hooks
3. **Advanced**: Review `search_shortcuts/` - includes menu actions

### Common Questions

**Q: How do I access the browser from my addon?**  
A: Use `self.browser_instance` which is set during `init()`:
```python
current_tab = self.browser_instance.tabs.currentWidget()
url = current_tab.url().toString()
```

**Q: How do I store addon settings?**  
A: Save data in your addon folder:
```python
import os, json
addon_dir = os.path.dirname(__file__)
with open(os.path.join(addon_dir, "settings.json"), "w") as f:
    json.dump(settings, f)
```

**Q: How do I add menu items?**  
A: Implement `get_menu_actions()`:
```python
def get_menu_actions(self):
    return [{
        "menu": "Tools",
        "label": "My Action",
        "callback": self.my_action_handler
    }]

def my_action_handler(self):
    print("Action clicked!")
```

**Q: Can I use PyQt5 in my addon?**  
A: Yes! The browser uses PyQt5, so you can import and use it:
```python
from PyQt5.QtWidgets import QMessageBox
QMessageBox.information(self.browser_instance, "Title", "Message")
```

**Q: How do I debug my addon?**  
A: Use `print()` statements - output appears in console:
```python
print("Debug: Something happened")  # Visible in terminal/console
```

## Contributing

To contribute add-ons to the community:

1. Organize in a folder with `manifest.json`
2. Test thoroughly with multiple browser operations
3. Include documentation in your addon folder
4. Include license information in manifest.json
5. Create a GitHub repository if sharing publicly
6. Submit with example usage and installation instructions
