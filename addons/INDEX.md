# HHBrowser Add-ons Directory

Welcome to the HHBrowser Add-on System! This directory contains all add-ons and documentation.

## 📖 Documentation (Read These!)

Start with one of these based on your needs:

### For Users
- **[README.md](README.md)** - Main guide with quick start and troubleshooting
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet

### For Developers
- **[README.md](README.md)** - User guide has development section
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed technical guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Code snippets and examples

## 🔧 Getting Started

### Users: Managing Add-ons
1. Open HHBrowser
2. Go to `Tools > Add-ons > Manage Add-ons`
3. Enable or disable add-ons
4. Use add-on features from the `Tools` menu

### Developers: Creating Add-ons
1. Copy the `template/` folder: `cp -r template my_addon`
2. Edit `manifest.json` with your add-on info
3. Edit `addon.py` with your code
4. Reload: `Tools > Add-ons > Reload Add-ons`
5. Test: `Tools > Add-ons > Manage Add-ons` → Enable your add-on

## 📁 Directory Structure

```
addons/
├── README.md                 ← START HERE
├── SETUP_GUIDE.md            ← Technical details
├── QUICK_REFERENCE.md        ← Cheat sheet
├── addons.json               (auto-managed, don't edit)
│
├── page_info/                Example add-on #1
│   ├── manifest.json
│   └── addon.py
│
├── session_logger/           Example add-on #2
│   ├── manifest.json
│   └── addon.py
│
├── search_shortcuts/         Example add-on #3
│   ├── manifest.json
│   └── addon.py
│
└── template/                 Use this to create new add-ons
    ├── manifest.json
    ├── addon.py
    └── README.md
```

## ✨ Example Add-ons

Three fully functional example add-ons are included:

### Page Info Display (`page_info/`)
Shows page load information and statistics. Perfect for learning basic hooks.
- **Status**: Enabled by default
- **Features**: Displays page title, URL, and load time
- **Menu**: Tools > Show Current Page Stats

### Session Logger (`session_logger/`)
Logs all browser events to a file. Shows how to use all available hooks.
- **Status**: Enabled by default
- **Features**: Tracks tabs, navigation, page loads, downloads
- **Log File**: `addons/session_logger/session_log.txt`

### Search Shortcuts (`search_shortcuts/`)
Quick access to multiple search engines. Shows UI integration.
- **Status**: Enabled by default
- **Features**: Search with Google, DuckDuckGo, Bing, GitHub, Wikipedia, YouTube
- **Menu**: Tools > Search [Engine Name]...

## 🚀 Quick Commands

```bash
# Test your manifest.json is valid JSON
python -m json.tool addons/my_addon/manifest.json

# Test your Python file has no syntax errors
python -m py_compile addons/my_addon/addon.py

# Create new add-on from template
cp -r template my_addon
```

## 📋 Add-on Checklist

When creating a new add-on, verify:

- [ ] Folder exists: `addons/my_addon/`
- [ ] `manifest.json` exists in folder
- [ ] `addon.py` exists in folder
- [ ] `manifest.json` has all required fields
- [ ] `addon.py` has class inheriting from `HBrowserAddon`
- [ ] `init()` method returns `True`
- [ ] `unload()` method returns `True`
- [ ] Tested and working

## ❓ Troubleshooting

### Add-on doesn't appear in Manage Add-ons
1. Check `manifest.json` exists and is valid JSON
2. Verify folder structure: `addons/addon_name/manifest.json`
3. Reload: `Tools > Add-ons > Reload Add-ons`

### Add-on won't enable
1. Check console for error messages
2. Verify `addon.py` file exists
3. Verify class inherits from `HBrowserAddon`
4. Check `init()` returns `True`

### Features don't work
1. Add `print()` statements for debugging
2. Run HHBrowser from terminal to see output
3. Check hook method names and signatures

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting.

## 📚 Learning Resources

### Study These Examples
1. **page_info/** - Start here, simplest example
2. **session_logger/** - Uses all hooks
3. **search_shortcuts/** - Shows UI integration

### Recommended Reading Order
1. [README.md](README.md) - 10 minutes
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 5 minutes
3. Study `template/addon.py` - 5 minutes
4. Create your first add-on - 30 minutes

## 🎓 Full Documentation

For complete information on:
- **Quick start**: See [README.md](README.md)
- **Technical details**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Code examples**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Template**: See [template/addon.py](template/addon.py)

## 📝 Notes

- All add-ons must be in **folders** (not loose .py files)
- Each add-on folder **must** have `manifest.json`
- `manifest.json` **must** be valid JSON
- The Python file with your addon class is specified in `manifest.json` under `"main"`

## 🆘 Need Help?

1. **Read the documentation first** - Most questions are answered there
2. **Check the examples** - page_info, session_logger, search_shortcuts
3. **Validate your files** - Use `python -m json.tool` and `python -m py_compile`
4. **Check the console** - Run from terminal to see `print()` output
5. **Review SETUP_GUIDE.md** - Has detailed debugging section

---

**Happy add-on development! 🎉**
