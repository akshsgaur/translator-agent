# Language Tutor - Installation Guide

## Requirements

Before installing Language Tutor, you need to install **Ollama** to run AI models locally.

### Step 1: Install Ollama

1. Visit [https://ollama.com/download](https://ollama.com/download)
2. Click "Download for macOS"
3. Open the downloaded file and drag Ollama to your Applications folder
4. Open Ollama from Applications (it will run in the menu bar)

### Step 2: Download Required AI Models

Open Terminal and run these commands to download the required models:

```bash
# Translation model (required)
ollama pull llama3.2

# Or use the specialized translation model (recommended)
ollama pull translategemma:4b
```

### Step 3: Install Language Tutor

#### Option A: Using the DMG Installer
1. Open `LanguageTutor.dmg`
2. Drag `Language Tutor.app` to the Applications folder
3. Eject the disk image

#### Option B: Direct App Installation
1. Drag `LanguageTutor.app` to your Applications folder

### Step 4: First Launch

Since this app is not signed with an Apple Developer certificate, macOS will show a security warning on first launch.

**To open the app:**

1. Right-click (or Control-click) on `Language Tutor.app`
2. Select "Open" from the context menu
3. Click "Open" in the security dialog

You only need to do this once. After that, the app will open normally.

**Alternative method:**
1. Try to open the app normally (it will be blocked)
2. Go to **System Settings → Privacy & Security**
3. Scroll down to find "Language Tutor was blocked"
4. Click "Open Anyway"

---

## Troubleshooting

### "Ollama is not running" error

1. Make sure Ollama is open (check for the llama icon in your menu bar)
2. If not running, open Ollama from Applications

### "Model not found" error

Open Terminal and download the required model:
```bash
ollama pull llama3.2
```

### App crashes on startup

1. Make sure you have macOS 10.15 (Catalina) or later
2. Try deleting the app and reinstalling
3. Check if Ollama is running properly

### Slow responses

- First response may be slow as the model loads into memory
- Subsequent responses should be faster
- Larger models require more RAM and may be slower on older Macs

---

## Uninstalling

1. Quit Language Tutor
2. Drag `Language Tutor.app` from Applications to Trash
3. (Optional) Remove user data: `rm -rf ~/Library/Application Support/LanguageTutor`

To also uninstall Ollama:
1. Quit Ollama from the menu bar
2. Drag Ollama from Applications to Trash
3. (Optional) Remove models: `rm -rf ~/.ollama`

---

## Support

For issues and feature requests, please visit the project repository.
