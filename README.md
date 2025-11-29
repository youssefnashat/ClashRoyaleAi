# Clash Royale Match Analyzer

A Python-based tool for recording and analyzing Clash Royale matches from an Android emulator.

## Setup

### First Time

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python -m pip install --upgrade pywin32
```

### Every Time

```powershell
.\.venv\Scripts\Activate
python functions/vision.py
```

## Troubleshooting

**"Module not found" errors**
- Ensure virtual environment is activated: `.\.venv\Scripts\Activate`
- Run `pip install -r requirements.txt`

**VS Code can't find imports**
- Restart VS Code
- Set interpreter to `.\.venv\Scripts\python.exe`
