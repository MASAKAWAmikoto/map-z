# 🗺️ Thailand Live Population Map

A Flask app that shows all 77 Thai provinces as an interactive heatmap. Add/remove people per province and watch the colors shift from blue (empty) to red (crowded).

## Deploy on Render (free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn thai_map_app:app`
5. Hit **Deploy** — done!

## Run locally

```bash
pip install flask
python thai_map_app.py
```
Then open http://localhost:5000
