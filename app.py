import base64
import io
from urllib.parse import quote, urlparse

import qrcode
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Short Link + QR</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 520px; margin: 40px auto; padding: 0 16px; }
    input[type=text] { width: 100%; padding: 10px; font-size: 16px; box-sizing: border-box; }
    button { margin-top: 10px; padding: 10px 18px; font-size: 16px; cursor: pointer; }
    .result { margin-top: 24px; padding: 16px; border: 1px solid #ccc; border-radius: 8px; }
    .error { color: #b00020; margin-top: 16px; }
    img { max-width: 220px; display: block; margin-top: 12px; }
  </style>
</head>
<body>
  <h2>Shorten a URL + get a QR code</h2>
  <form method="post">
    <input type="text" name="url" placeholder="Paste your long URL here" value="{{ long_url or '' }}" required>
    <button type="submit">Shorten</button>
  </form>

  {% if error %}<div class="error">{{ error }}</div>{% endif %}

  {% if short_url %}
  <div class="result">
    <div>Short link: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a></div>
    <img src="data:image/png;base64,{{ qr_b64 }}" alt="QR code">
    <a download="qr.png" href="data:image/png;base64,{{ qr_b64 }}">Download QR</a>
  </div>
  {% endif %}
</body>
</html>
"""


def is_valid_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.netloc)


def shorten_with_tinyurl(long_url: str) -> str:
    # Simple TinyURL endpoint, no API key required
    r = requests.get(
        f"https://tinyurl.com/api-create.php?url={quote(long_url, safe='')}",
        timeout=10,
    )
    r.raise_for_status()
    return r.text.strip()


def make_qr_base64(data: str) -> str:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@app.route("/", methods=["GET", "POST"])
def index():
    ctx = {"long_url": None, "short_url": None, "qr_b64": None, "error": None}

    if request.method == "POST":
        long_url = request.form.get("url", "").strip()
        if long_url and "://" not in long_url:
            long_url = "https://" + long_url
        ctx["long_url"] = long_url

        if not is_valid_url(long_url):
            ctx["error"] = "Please enter a valid URL."
        else:
            try:
                short = shorten_with_tinyurl(long_url)
                ctx["short_url"] = short
                ctx["qr_b64"] = make_qr_base64(short)
            except requests.RequestException:
                ctx["error"] = "Couldn't reach TinyURL. Try again in a moment."

    return render_template_string(PAGE, **ctx)


if __name__ == "__main__":
    app.run(debug=True)
