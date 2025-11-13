# 🎮 RomSort

<div align="center">

**An intelligent ROM file organizer with smart region-based matching**

*Automatically find and move the best ROM versions from massive collections*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Features

### 🧠 Smart ROM Matching
- **Symbol-insensitive** - Matches "Castlevania: Rondo" with "Castlevania - Rondo"
- **Flexible name variants** - Handles subtitles, "The" prefix, partial names
- **Fuzzy matching** - Finds ROMs even with slight name differences
- **Word coverage scoring** - Prioritizes best title matches

### 🌍 Intelligent Region Priority System
**Automatic preference order:**
1. **Europe** - Highest priority (includes EU, Europe)
2. **USA** - Second priority (includes US, USA)
3. **World** - Third priority
4. **English** - Fourth priority (includes En, English)
5. **Rejects Japan-only** - Unless combined with acceptable regions

### 🚫 Advanced Filtering
**Automatically rejects unwanted versions:**
- Beta, Prototype, Alpha, Demo
- Virtual Console (Wii U, Wii, Switch Online)
- Alt versions (Alt, Alt 1, Alt 2, Alt 3)
- Revisions (Rev, Rev 1, V1.0, V2.0)
- Samples, Promos, Hacks, Homebrew
- Invalid second parentheses (e.g., `(USA) (Alt 2)`)

### 📊 Detailed Results Display
- Shows **exact file selected** and why
- Lists **alternative candidates** with scores
- Explains **rejections** (Japan-only, unwanted tags, etc.)
- Displays **"not found"** reasons (no matches vs. all rejected)

### ⚡ User-Friendly Interface
- **Multi-threaded processing** - UI stays responsive
- **Progress tracking** - Real-time status updates
- **Batch processing** - Handle hundreds of ROMs at once
- **Clear results** - Easy-to-read success/failure summary

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (tested on Python 3.13)
- Windows/macOS/Linux

### Installation

```bash
# Clone or download the repository
cd RomSort

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python mass_file_mover.py
```

---

## 🎮 How to Use

### 1️⃣ Select Directories
- **Source Directory**: Folder containing all your ROM files
- **Target Directory**: Where selected ROMs will be moved

### 2️⃣ Enter ROM Names
Type or paste ROM names in the text area (one per line):
```
Super Metroid
Castlevania: Rondo of Blood
Bonk's Adventure
Alien Crush
Street Fighter II Turbo
```

### 3️⃣ Process
- Click **Start Processing**
- Watch real-time progress
- Review detailed results

### 4️⃣ Check Results
Results show:
- ✓ Successfully moved files with exact filename
- Alternative candidates considered
- ✗ Not found with explanation
- Summary statistics

---

## 🎯 Matching Examples

### Example 1: Region Priority
**Search:** `Super Metroid`

**Found:**
- `Super Metroid (Europe) (En,Fr,De).zip` ← **SELECTED** (Europe priority)
- `Super Metroid (Japan, USA) (En,Ja).zip` (score: 1696)
- `Super Metroid (USA).zip` (score: 1046)

### Example 2: Filtering Unwanted
**Search:** `Bonk's Revenge`

**Found:**
- `Bonk's Revenge (USA).zip` ← **SELECTED** (clean version)
- `Bonk's Revenge (USA) (Alt 2).zip` (rejected: Alt version)
- `Bonk's Revenge (Europe) (Rev 1).zip` (rejected: Revision)

### Example 3: Symbol Flexibility
**Search:** `Dragon's Curse (Wonder Boy III)`

**Matches:**
- `Dragons Curse - Wonder Boy 3.zip` (punctuation ignored)
- `Dragon's Curse (USA).zip` (exact match prioritized)

---

## 🔍 Valid ROM Name Patterns

### ✅ Accepted Formats
```
ROM NAME (Europe)
ROM NAME (USA)
ROM NAME (World)
ROM NAME (Europe, USA)
ROM NAME (Japan) (En)
ROM NAME (Japan, USA)
ROM NAME (En)
ROM NAME (English)
```

### ❌ Rejected Formats
```
ROM NAME (Japan)                    # Japan-only
ROM NAME (USA) (Alt 2)              # Alternative version
ROM NAME (Europe) (Rev 1)           # Revision
ROM NAME (World) (Wii Virtual Console)  # Virtual Console
ROM NAME (USA) (Beta)               # Beta version
```

---

## 📦 Dependencies

```
PyQt6>=6.4.0
```

---

## 🗂️ Project Structure

```
RomSort/
├── mass_file_mover.py    # Main application
├── requirements.txt      # Dependencies
├── README.md            # You are here!
└── .gitignore          # Git ignore rules
```

---

## 💡 Tips & Tricks

### For Large Collections
- Use the exact names you want (app handles variations)
- Check "Other candidates" to see what else was available
- Review rejected files to understand filtering

### For Best Results
- Use simple names (app handles subtitle matching)
- Don't worry about punctuation (`:` vs `-` vs nothing)
- Trust the region priority (Europe > USA > World > En)

### Common Use Cases
- **ROM Set Curation**: Extract only the best versions
- **Multi-Region Collections**: Prioritize your preferred region
- **Clean Duplicates**: Automatically skip Alt/Rev versions

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs or issues
- Suggest feature improvements
- Submit pull requests

---

## 📄 License

MIT License - Free to use and modify

---

## 👨‍💻 Author

**CodeKokeshi** (Kokeshi Aikawa)

- Other projects: 
  - [Kokesynth](https://github.com/CodeKokeshi/Kokesynth) - 16-bit retro synthesizer
  - [Kokesprite](https://github.com/CodeKokeshi/Kokesprite) - Pixel art editor
  - [MeterSnap](https://github.com/CodeKokeshi/MeterSnap) - Screenshot utility
- Style: Practical tools with intelligent automation

---

## 🎉 Acknowledgments

- Inspired by the ROM preservation community
- Built for retro gaming enthusiasts
- Special thanks to No-Intro and Redump projects

---

<div align="center">

**Happy ROM organizing! 🎮✨**

*Let the algorithm find the best versions for you!*

</div>
