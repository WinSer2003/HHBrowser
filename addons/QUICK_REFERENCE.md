# HHBrowser Add-on System - Quick Reference

## Key Rules ⚠️

1. **Addons MUST be in folders** - Not loose .py files
2. **manifest.json REQUIRED** - In addon root folder
3. **addon.py required** - With class inheriting from `HBrowserAddon`
4. **init() and unload() required** - Must return bool

## Minimum Addon

```
addons/my_addon/
├── manifest.json
└── addon.py
```

### manifest.json
```json
{
  "name": "My Addon",
  "version": "1.0.0",
  "description": "Does something",
  "author": "You",
  "main": "addon.py"
}
```

### addon.py
```python
from addon_system import HBrowserAddon

class MyAddon(HBrowserAddon):
    def init(self, browser_instance) -> bool:
        self.browser_instance = browser_instance
        return True
    
    def unload(self) -> bool:
        return True
```

## Event Hooks

```python
def on_tab_created(self, tab_index: int, browser_widget) -> None: pass
def on_tab_closed(self, tab_index: int) -> None: pass
def on_url_changed(self, url: str) -> None: pass
def on_page_loaded(self, url: str, title: str) -> None: pass
def on_download_started(self, filename: str, path: str) -> None: pass
```

## Menu Actions

```python
def get_menu_actions(self):
    return [{
        "menu": "Tools",
        "label": "My Action",
        "callback": self.action_handler
    }]

def action_handler(self):
    print("Clicked!")
```

## Browser Access

```python
# Get current tab
tab = self.browser_instance.tabs.currentWidget()

# Get URL
url = tab.url().toString()

# Get title
title = tab.page().title()

# Navigate
from PyQt5.QtCore import QUrl
tab.setUrl(QUrl("https://example.com"))
```

## File Storage

```python
import os, json

# Get addon folder
addon_dir = os.path.dirname(__file__)

# Save data
data = {"key": "value"}
with open(os.path.join(addon_dir, "data.json"), "w") as f:
    json.dump(data, f)

# Load data
with open(os.path.join(addon_dir, "data.json")) as f:
    data = json.load(f)
```

## Debugging

```python
# Print to console (visible when running from terminal)
print(f"Debug: {variable}")

# Check manifest syntax
python -m json.tool addons/my_addon/manifest.json

# Check Python syntax
python -m py_compile addons/my_addon/addon.py

# Run browser from terminal to see output
python HHBrowser.py
```

## Testing Steps

1. Create addon folder with manifest.json and addon.py
2. `Tools > Add-ons > Reload Add-ons`
3. `Tools > Add-ons > Manage Add-ons`
4. Enable addon
5. Check console for output
6. Test features

## Common Mistakes

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| Loose .py file | Addon in folder |
| No manifest.json | manifest.json in folder |
| `"main": "__init__.py"` | `"main": "addon.py"` |
| `init()` no return | `return True` |
| Hooks are named wrong | Use exact names from docs |
| Missing import | `from addon_system import HBrowserAddon` |

## Available Menus

- "File"
- "Tools" ← Most common
- "View"
- "History"
- "Bookmarks"
- "Settings"
- "Downloads"
- "Add-ons"

## Resources

- **README.md** - User-friendly guide
- **SETUP_GUIDE.md** - Technical details
- **template/** - Copy to create new addon
- **page_info/** - Simple example
- **session_logger/** - All hooks example
- **search_shortcuts/** - UI example

## Need Help?

1. Check console output (`print()` statements)
2. Review examples in `addons/`
3. Read SETUP_GUIDE.md troubleshooting section
4. Validate manifest with: `python -m json.tool addons/my_addon/manifest.json`
5. Check Python syntax: `python -m py_compile addons/my_addon/addon.py`
