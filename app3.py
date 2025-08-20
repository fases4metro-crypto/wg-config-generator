from flask import Flask, render_template_string, request, send_file
import secrets, base64, io

app = Flask(__name__)

def generate_random_ip():
    first_octet = secrets.randbelow(256)
    second_octet = secrets.randbelow(256)
    third_octet = secrets.randbelow(256)
    return f"{first_octet}.{second_octet}.{third_octet}.0/24"

def generate_random_dns():
    random_dns = f"{secrets.randbelow(256)}.{secrets.randbelow(256)}.{secrets.randbelow(256)}.{secrets.randbelow(256)}"
    return f"{random_dns}, 10.202.10.10"

def generate_random_private_key():
    key = secrets.token_bytes(32)
    return base64.b64encode(key).decode("utf-8")

def generate_config():
    return (
        "[Interface]\n"
        f"PrivateKey = {generate_random_private_key()}\n"
        f"Address = {generate_random_ip()}\n"
        f"DNS = {generate_random_dns()}\n"
        f"MTU = {secrets.randbelow(100) + 1300}\n"
        f"ListenPort = {secrets.randbelow(40000) + 10000}"
    )

html = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WireGuard Config Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center">
    <div class="bg-gray-800 rounded-2xl shadow-2xl p-8 max-w-xl w-full border border-purple-600">
        <h1 class="text-3xl font-bold text-center text-purple-400 mb-6 animate-pulse">⚡ WireGuard Config Generator ⚡</h1>
        <form method="post" class="flex flex-col space-y-4">
            <input type="text" name="filename" placeholder="Enter config filename" required
                class="w-full p-3 rounded-lg bg-gray-700 border border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-400 text-white">
            <button type="submit"
                class="py-3 rounded-lg bg-gradient-to-r from-purple-600 to-green-500 hover:scale-105 transform transition text-lg font-semibold shadow-lg">
                Generate Config
            </button>
        </form>
        {% if config %}
        <div class="mt-6">
            <h2 class="text-xl font-bold text-green-400 mb-2">✅ Config Generated:</h2>
            <pre class="bg-black text-green-400 p-4 rounded-lg overflow-x-auto border border-green-500">{{ config }}</pre>
            <a href="/download/{{ filename }}" 
               class="mt-4 block text-center py-3 rounded-lg bg-gradient-to-r from-green-600 to-purple-500 hover:scale-105 transform transition text-lg font-semibold shadow-lg">
               ⬇️ Download Config
            </a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    config = None
    filename = None
    if request.method == "POST":
        filename = request.form.get("filename", "wg_fake")
        config = generate_config()
        # ذخیره در حافظه برای دانلود
        app.config["last_config"] = (filename, config)
    return render_template_string(html, config=config, filename=filename)

@app.route("/download/<filename>")
def download(filename):
    # گرفتن آخرین کانفیگ از حافظه
    fname, config = app.config.get("last_config", ("wg_fake", ""))
    buf = io.BytesIO(config.encode("utf-8"))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"{fname}.conf", mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)