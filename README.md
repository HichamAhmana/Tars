# TARS - Advanced Voice Assistant

TARS is a powerful, Jarvis-inspired PC assistant designed to give you hands-free control over your Windows machine. Built with a modular Python engine, a Django backend, and a modern Next.js dashboard, TARS bridges the gap between simple voice commands and complex system automation.

![TARS Banner](https://img.shields.io/badge/TARS-Voice%20Assistant-blue?style=for-the-badge)

## 🌟 Key Features

- **Wake Word Activation**: Powered by "Tars" (customizable in config).
- **Application Control**: Launch and kill any Windows application (Spotify, Discord, VS Code, etc.).
- **Web Intelligence**: Search Google, browse YouTube, or navigate to any website via voice.
- **Media Mastery**: Control playback, skip tracks, and adjust volume across the system.
- **Window Management**: Minimize, maximize, snap, and switch windows with simple commands.
- **System Automation**: Shutdown, restart, lock PC, check battery, and empty recycle bin.
- **Voice Dictation**: Directly type text into any active field using voice.
- **Monitoring Dashboard**: A glassmorphic Next.js interface to track command history and manage settings.

## 🏗️ Project Structure

- **`engine/`**: The core Python voice engine. Handles speech-to-text, command parsing, and text-to-speech.
- **`backend/`**: Django-powered REST API for orchestration and data management.
- **`dashboard/`**: Next.js frontend for real-time monitoring and visual control.
- **`api/`**: Logic layer and API integrations.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js & npm (for the dashboard)
- Windows OS (optimized for Windows shortcuts)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HichamAhmana/Tars.git
   cd Tars
   ```

2. **Setup the Voice Engine**:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/Scripts/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Setup the Dashboard**:
   ```bash
   cd dashboard
   npm install
   ```

### Running TARS

You can start the entire ecosystem using the provided batch script:
```bash
./start.bat
```

Or run the components individually:
- **Engine**: `python engine/main.py`
- **Backend**: `python manage.py runserver`
- **Dashboard**: `cd dashboard && npm run dev`

## ⚙️ Configuration

Customize TARS's behavior in `engine/config.py`:
- `WAKE_WORD`: Change the word that triggers TARS.
- `TTS_RATE`: Adjust the speaking speed.
- `CUSTOM_APPS`: Map spoken names to specific executables.

---
*Built with ❤️ for productivity.*
