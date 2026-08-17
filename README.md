# Minimal Flask App

## Setup (Windows)

1. Create a virtualenv and activate it:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1  # or venv\Scripts\activate for cmd
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

To listen on all interfaces (useful for testing from other devices), edit `app.run` in `app.py` to:

```py
app.run(host='0.0.0.0', port=5000, debug=True)
```
