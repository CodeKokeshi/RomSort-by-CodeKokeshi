# 🎮 RomSort by CodeKokeshi

<div align="center">

**Lightning-fast ROM organizer for RetroAchievements compatibility**

*Exact-match file finder - no fuzzy logic, no guesswork*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Features

### ⚡ Exact Match Only
- **Character-perfect matching** - No fuzzy logic, no approximations
- **Extension-agnostic** - Matches `.sfc`, `.smc`, `.zip`, etc. automatically
- **RetroAchievements optimized** - Built specifically for RA ROM lists
- **Instant file indexing** - O(1) hash-based lookups for massive romsets

### 🎯 Simple & Fast
- **One-to-one matching** - If the name matches exactly (minus extension), it moves
- **No complex settings** - No region priorities, no filtering rules
- **Lightning fast** - Processes thousands of ROMs in seconds
- **Real-time progress** - Multi-threaded with responsive UI

### 📊 Clear Results
- Shows **moved files** with full filenames
- Reports **not found** with similar candidates for debugging
- Displays **failed moves** with error details
- Complete **summary statistics** at the end

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PyQt6

### Installation

```bash
# Clone the repository
git clone https://github.com/CodeKokeshi/RomSort-by-CodeKokeshi.git
cd RomSort-by-CodeKokeshi

# Install dependencies
pip install -r requirements.txt

# Run the app
python mass_file_mover.py
```

---

## 📖 Usage Guide

### Step-by-Step

1. **Get your RA list** 
   - Go to RetroAchievements and find your console
   - Manually scrape the supported ROM names from game pages
   - Copy the exact names (with or without trailing dots)

2. **Select Source Directory**
   - Choose folder with your complete romset (No-Intro, Redump, etc.)

3. **Select Target Directory**
   - Choose where matched ROMs should be moved

4. **Paste ROM Names**
   - Paste your RA list into the text area (one per line)
   - Trailing dots are automatically handled

5. **Start Processing**
   - Click "Start Processing" and watch it work!

### Example Input Format

```
Super Mario World (USA).
Legend of Zelda, The - A Link to the Past (USA).
Super Metroid (Japan, USA) (En,Ja).
Mega Man X (USA) (Rev 1).
Kirby Super Star (USA)
```

*Note: Both formats work - with or without trailing dots*

---

## 🎯 How It Works

### Matching Algorithm

```
1. Build file index: "Super Mario World (USA).sfc" → "Super Mario World (USA)"
2. Clean ROM name: "Super Mario World (USA)." → "Super Mario World (USA)"
3. Exact match: "Super Mario World (USA)" == "Super Mario World (USA)" ✓
4. Move file: Super Mario World (USA).sfc → Target Directory
```

### What Gets Matched

| ROM Name (Input) | Filename (Source) | Match? |
|---|---|---|
| `Super Mario World (USA)` | `Super Mario World (USA).sfc` | ✅ Yes |
| `Super Mario World (USA)` | `Super Mario World (USA).smc` | ✅ Yes |
| `Super Mario World (USA)` | `Super Mario World (USA).zip` | ✅ Yes |
| `Super Mario World (USA)` | `Super Mario World (Europe).sfc` | ❌ No |
| `Super Mario World (USA)` | `Super Mario World (USA) (Rev 1).sfc` | ❌ No |

---

## 📊 Example Output

```
=== PROCESSING COMPLETE ===

✓ MOVED: Super Mario World (USA)
  └─ File: Super Mario World (USA).sfc

✓ MOVED: Legend of Zelda, The - A Link to the Past (USA)
  └─ File: Legend of Zelda, The - A Link to the Past (USA).smc

✗ NOT FOUND: Mega Man X (USA) (Rev 1)
  └─ Similar files found (but not exact matches):
     • Mega Man X (USA)
     • Mega Man X (USA) (Rev 2)
     • Mega Man X2 (USA)

✓ MOVED: Kirby Super Star (USA)
  └─ File: Kirby Super Star (USA).sfc

============================================================
✓ Successfully moved: 3
✗ Failed to move: 0
✗ Not found: 1
============================================================
```

---

## 🎮 Perfect for RetroAchievements

### Why Use RomSort?

**The Problem:**
- You download a 10GB No-Intro romset with 5,000+ games
- Only ~500 have RetroAchievements support
- Manually finding supported versions takes hours

**The Solution:**
1. Scrape RA's supported ROM names (5 minutes)
2. Paste into RomSort (5 seconds)
3. Get achievement-compatible collection (30 seconds)

### Typical Workflow

```
1. Download complete SNES No-Intro set (~5,000 games)
2. Visit RetroAchievements SNES page
3. Copy supported game names from RA
4. Paste into RomSort
5. Get clean folder with ~500 RA-compatible ROMs
6. Load into RetroArch and start earning achievements!
```

---

## 🛠️ Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Threading**: QThread for non-blocking operations
- **File Operations**: `shutil.move` with error handling
- **Algorithm**: Hash-based O(1) file lookup
- **Matching**: Extension-stripped exact string comparison

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 👨‍💻 Author

**CodeKokeshi**

Building tools for retro gaming enthusiasts 🕹️

---

## 🤝 Contributing

Issues and feature requests are welcome!

Found a bug? [Open an issue](https://github.com/CodeKokeshi/RomSort-by-CodeKokeshi/issues)

---

## ⭐ Show Your Support

If RomSort helped you build your achievement-compatible ROM collection, give it a ⭐️!

---

<div align="center">

**Made with ❤️ for the RetroAchievements community**

</div>
