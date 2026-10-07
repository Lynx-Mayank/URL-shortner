# URL-shortner + QR Generator
## Website Link - https://url-shortner-uc5p.onrender.com/  ###(the website make take 50s to load)

A simple Flask web app that turns a long URL into a short link (via TinyURL) and generates a downloadable QR code for it.

## Features

- Shorten any long URL using TinyURL (no API key needed)
- Instantly generate a QR code for the short link
- Download the QR code as a PNG
- Basic URL validation and error handling
- Single-file app, no database required

## Tech Stack

- Python 3
- Flask
- Requests
- qrcode (with Pillow)
- Gunicorn (for deployment)

## Project Structure

```
url-shortener/
├── app.py
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/url-shortener.git
cd url-shortener
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Usage

1. Paste a long URL into the input box.
2. Click **Shorten**.
3. Copy the short link or scan/download the QR code.

## Deployment (Render)

1. Push this project to a GitHub repository.
2. On [Render](https://render.com), create a new **Web Service** and connect the repo.
3. Use these settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Deploy. Note that on the free tier the app sleeps after inactivity, so the first load may take up to a minute.

## Notes

- This app uses TinyURL's simple public endpoint. For heavy use, consider switching to the official TinyURL or Bitly API with an API token.
- The QR code encodes the shortened link, not the original URL.

## Future Improvements

- Copy-to-clipboard button
- Custom aliases for short links
- Bitly API support
- Scan history

## License

MIT
