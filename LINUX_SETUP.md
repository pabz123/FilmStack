# MovieFlix – Linux (Ubuntu) Setup Guide

This guide explains how to run **MovieFlix** on Ubuntu and other Debian-based
Linux distributions, and how to integrate **GitHub Copilot CLI** into your
Ubuntu terminal.

---

## Table of Contents

1. [Running MovieFlix on Ubuntu](#1-running-movieflix-on-ubuntu)
2. [Building a Standalone Linux Executable](#2-building-a-standalone-linux-executable)
3. [Setting Up GitHub Copilot CLI on Ubuntu](#3-setting-up-github-copilot-cli-on-ubuntu)

---

## 1. Running MovieFlix on Ubuntu

### Prerequisites

```bash
# System packages
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-pyqt5 vlc git -y
```

> **Note:** VLC is required for video playback. The app detects it
> automatically once installed.

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/pabz123/FilmStack.git
cd FilmStack

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy the example environment file
cp .env.example .env   # or create a .env with your TMDB_API_KEY

# 5. Start MovieFlix
python start_movieflix.py
```

### Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key_here
API_HOST=127.0.0.1
API_PORT=8765
```

Get a free TMDB API key at <https://www.themoviedb.org/settings/api>.

### Troubleshooting

| Problem | Solution |
|---------|---------|
| `ModuleNotFoundError: No module named 'vlc'` | `pip install python-vlc` and ensure VLC is installed: `sudo apt install vlc` |
| `cannot connect to X server` | Make sure you're running in a graphical session (not SSH without `-X`) |
| Backend port 8765 already in use | Kill the existing process: `fuser -k 8765/tcp` |
| PyQt5 display issues | Install Qt platform plugin: `sudo apt install libxcb-xinerama0` |

---

## 2. Building a Standalone Linux Executable

Use the included `build_linux.sh` script to create a self-contained
executable with PyInstaller.

```bash
# Make sure VLC and PyInstaller are installed
sudo apt install vlc
source venv/bin/activate
pip install pyinstaller

# Run the build script
chmod +x build_linux.sh
./build_linux.sh
```

The output will be in `dist/MovieFlix/` and a portable archive at
`dist/MovieFlix_Linux_v1.0.tar.gz`.

> **Note for end-users of the built executable:**
> VLC must still be installed on the target machine:
> `sudo apt install vlc`

---

## 3. Setting Up GitHub Copilot CLI on Ubuntu

GitHub Copilot CLI (`gh copilot`) lets you get AI-powered command
suggestions directly in your terminal.

### Step 1 – Install the GitHub CLI (`gh`)

```bash
# Import the GitHub CLI GPG key and apt source
(type -p wget >/dev/null || sudo apt install wget -y) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
     | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
     | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

### Step 2 – Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate via a browser or a personal access token.

### Step 3 – Install the Copilot CLI Extension

```bash
gh extension install github/gh-copilot
```

### Step 4 – Use Copilot in the Terminal

```bash
# Ask for a shell command suggestion
gh copilot suggest "find all mp4 files larger than 1 GB"

# Explain a command
gh copilot explain "tar -czf archive.tar.gz ./dist"
```

#### Optional: Create Handy Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Copilot shell suggestion alias
alias '??'='gh copilot suggest -t shell'

# Copilot command explanation alias
alias 'ghce'='gh copilot explain'
```

Then reload:

```bash
source ~/.bashrc
```

Now you can type `?? list all video files` in your terminal for instant
AI-powered command suggestions.

### Requirements

- Ubuntu 20.04 LTS or newer (22.04 / 24.04 recommended)
- An active **GitHub Copilot** subscription
  (Individual, Business, or Enterprise)
- `gh` CLI ≥ 2.30.0
