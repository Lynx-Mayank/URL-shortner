import base64
import io
from urllib.parse import quote, urlparse

import qrcode
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Paste the link to your tab icon image here (png / ico / svg).
FAVICON_URL = "/static/img.png"

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Short link + QR code</title>
  {% if favicon %}
  <link rel="icon" href="{{ favicon }}">
  <link rel="apple-touch-icon" href="{{ favicon }}">
  {% endif %}
  <script>
    (function () {
      var t = null;
      try { t = localStorage.getItem("theme"); } catch (e) {}
      if (t !== "light" && t !== "dark") {
        t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      document.documentElement.setAttribute("data-theme", t);
    })();
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #eef2f8;
      --surface: #ffffff;
      --ink: #14213d;
      --muted: #5b6b82;
      --line: #d5deeb;
      --accent: #2b59ff;
      --accent-ink: #ffffff;
      --accent-soft: #e4ebff;
      --error: #c23b3b;
      --error-soft: #fbe9e9;
      --shadow: 0 1px 2px rgba(20, 33, 61, .06), 0 12px 32px rgba(20, 33, 61, .08);
    }
    :root { color-scheme: light; }
    :root[data-theme="dark"] {
        color-scheme: dark;
        --bg: #0e1526;
        --surface: #17203a;
        --ink: #e9eefb;
        --muted: #9aa9c4;
        --line: #2a3657;
        --accent: #6f8dff;
        --accent-ink: #0e1526;
        --accent-soft: #232f55;
        --error: #ff8a8a;
        --error-soft: #3a2230;
        --shadow: 0 12px 32px rgba(0, 0, 0, .35);
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; }
    body {
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
      font-size: 16px;
      line-height: 1.5;
      display: flex;
      justify-content: center;
      padding: 56px 20px 40px;
    }
    main { width: 100%; max-width: 560px; }

    h1 {
      font-family: "Bricolage Grotesque", "DM Sans", system-ui, sans-serif;
      font-weight: 700;
      font-size: clamp(2rem, 6vw, 2.75rem);
      line-height: 1.05;
      letter-spacing: -0.02em;
      margin: 0 0 12px;
    }
    .lede { margin: 0 0 32px; color: var(--muted); max-width: 44ch; }

    .field {
      display: flex;
      gap: 8px;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: 16px;
      padding: 8px;
      box-shadow: var(--shadow);
      transition: border-color .15s;
    }
    .field:focus-within { border-color: var(--accent); }
    .field input {
      flex: 1;
      min-width: 0;
      border: 0;
      outline: 0;
      background: transparent;
      color: var(--ink);
      font: inherit;
      padding: 12px 12px;
    }
    .field input::placeholder { color: var(--muted); opacity: .8; }

    .btn {
      font: inherit;
      font-weight: 600;
      border: 0;
      border-radius: 10px;
      padding: 12px 20px;
      cursor: pointer;
      background: var(--accent);
      color: var(--accent-ink);
      transition: transform .1s, opacity .15s;
    }
    .btn:hover { opacity: .92; }
    .btn:active { transform: translateY(1px); }
    .btn:disabled { opacity: .6; cursor: progress; }
    .btn.ghost {
      background: var(--accent-soft);
      color: var(--accent);
      padding: 9px 14px;
      font-size: .9rem;
      text-decoration: none;
      display: inline-block;
    }
    :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }

    .error {
      margin-top: 16px;
      padding: 12px 14px;
      border-radius: 12px;
      background: var(--error-soft);
      color: var(--error);
      font-weight: 500;
    }

    .result {
      margin-top: 28px;
      background: var(--surface);
      border: 1.5px solid var(--line);
      border-radius: 20px;
      padding: 24px;
      box-shadow: var(--shadow);
      display: grid;
      grid-template-columns: 200px 1fr;
      gap: 24px;
      align-items: center;
      animation: reveal .35s ease-out;
    }
    .qr {
      width: 200px;
      height: 200px;
      border-radius: 12px;
      background: #fff;
      padding: 10px;
      border: 1px solid var(--line);
    }
    .qr img { width: 100%; height: 100%; display: block; image-rendering: pixelated; }

    .label { color: var(--muted); font-size: .9rem; margin: 0 0 4px; }
    .short {
      font-family: "Bricolage Grotesque", "DM Sans", sans-serif;
      font-weight: 600;
      font-size: 1.4rem;
      letter-spacing: -0.01em;
      color: var(--ink);
      word-break: break-all;
      text-decoration: none;
      display: block;
      margin-bottom: 16px;
    }
    .short:hover { color: var(--accent); }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; }
    .origin {
      margin: 18px 0 0;
      font-size: .85rem;
      color: var(--muted);
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .result > div { min-width: 0; }

    .topbar { display: flex; justify-content: flex-end; margin-bottom: 20px; }
    .theme-toggle {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      border: 1.5px solid var(--line);
      background: var(--surface);
      color: var(--ink);
      display: grid;
      place-items: center;
      cursor: pointer;
      box-shadow: var(--shadow);
    }
    .theme-toggle:hover { color: var(--accent); }
    .theme-toggle svg { width: 20px; height: 20px; }
    .theme-toggle .moon { display: none; }
    :root[data-theme="dark"] .theme-toggle .sun { display: none; }
    :root[data-theme="dark"] .theme-toggle .moon { display: block; }

    footer { margin-top: 40px; color: var(--muted); font-size: .85rem; }

    @keyframes reveal { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    @media (prefers-reduced-motion: reduce) {
      .result { animation: none; }
      * { transition: none !important; }
    }
    @media (max-width: 520px) {
      body { padding-top: 36px; }
      .field { flex-direction: column; }
      .btn { width: 100%; }
      .result { grid-template-columns: 1fr; justify-items: center; text-align: center; }
      .actions { justify-content: center; }
      .qr { width: 220px; height: 220px; }
    }
  </style>
</head>
<body>
  <main>
    <div class="topbar">
      <button class="theme-toggle" type="button" id="theme" aria-label="Switch color theme" title="Switch color theme">
        <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
      </button>
    </div>
    <h1>Short link and QR code, in one step</h1>
    <p class="lede">Paste a long web address. You get a short link and a QR code that opens it.</p>

    <form method="post" id="form">
      <div class="field">
        <input type="text" name="url" inputmode="url" autocomplete="off" spellcheck="false"
               placeholder="Paste a long URL" aria-label="Long URL"
               value="{{ long_url or '' }}" required>
        <button class="btn" type="submit" id="submit">Shorten</button>
      </div>
    </form>

    {% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}

    {% if short_url %}
    <section class="result" aria-live="polite">
      <div class="qr"><img src="data:image/png;base64,{{ qr_b64 }}" alt="QR code for {{ short_url }}"></div>
      <div>
        <p class="label">Your short link</p>
        <a class="short" href="{{ short_url }}" target="_blank" rel="noopener" id="short">{{ short_url }}</a>
        <div class="actions">
          <button class="btn ghost" type="button" id="copy">Copy link</button>
          <a class="btn ghost" download="qr-code.png" href="data:image/png;base64,{{ qr_b64 }}">Download QR</a>
        </div>
        <p class="origin" title="{{ long_url }}">From {{ long_url }}</p>
      </div>
    </section>
    {% endif %}

    <footer>Links are shortened with TinyURL. The QR code points to the short link.</footer>
  </main>

  <script>
    const form = document.getElementById("form");
    const submit = document.getElementById("submit");
    form.addEventListener("submit", () => {
      submit.disabled = true;
      submit.textContent = "Shortening...";
    });

    document.getElementById("theme").addEventListener("click", () => {
      const root = document.documentElement;
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });

    const copyBtn = document.getElementById("copy");
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        const text = document.getElementById("short").textContent.trim();
        try {
          await navigator.clipboard.writeText(text);
        } catch (e) {
          const ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          ta.remove();
        }
        copyBtn.textContent = "Copied";
        setTimeout(() => (copyBtn.textContent = "Copy link"), 1800);
      });
    }
  </script>
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
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#14213d", back_color="white")
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
            ctx["error"] = "That doesn't look like a web address. Check it and try again."
        else:
            try:
                short = shorten_with_tinyurl(long_url)
                ctx["short_url"] = short
                ctx["qr_b64"] = make_qr_base64(short)
            except requests.RequestException:
                ctx["error"] = "TinyURL didn't respond. Wait a moment and try again."

    return render_template_string(PAGE, favicon=FAVICON_URL, **ctx)


if __name__ == "__main__":
    app.run(debug=True)
