# Emojiify Prototype (Flask)

This is a minimal prototype of the Emojiify MVP.
It supports:
- Uploading a photo → lightweight "emoji-style" PNG generated.
- Entering a short text prompt → simple emoji generated from prompt keywords.
- Download the generated PNG.

**How to run locally (recommended)**:

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows PowerShell
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
