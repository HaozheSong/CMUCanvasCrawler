Create a Python virtual environment
```bash
python3 -m venv pyvenv
source pyvenv/bin/activate

pip install -r requirements.txt
```
Create `cookie.py` and replace `"value": "cookie_value"` with your `canvas_session` cookie
```python
COOKIE = {
    "name": "canvas_session",
    "value": "cookie_value"
}
```
Run the crawler script
```bash
python crawler.py
```