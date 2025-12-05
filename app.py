from flask import Flask, render_template_string, request, send_from_directory
import os
from pypdf import PdfReader

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Iskanje v PDF-jih</title>
<h2>Iskanje po PDF-jih</h2>
<form method="POST">
    Pot do direktorija: <input type="text" name="folder" size="50"><br><br>
    Iskalne besede (ločene z vejico): <input type="text" name="keywords" size="50"><br><br>
    <input type="submit" value="Išči">
</form>

{% if results %}
<h3>Najdeni PDF-ji:</h3>
<ul>
{% for pdf in results %}
    <li><a href="{{ url_for('serve_file', folder=folder, filename=pdf) }}" target="_blank">{{ pdf }}</a></li>
{% endfor %}
</ul>
{% endif %}
"""


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    folder = ""
    if request.method == "POST":
        folder = request.form["folder"]
        keywords = [k.strip().lower() for k in request.form["keywords"].split(",") if k.strip()]
        if os.path.isdir(folder):
            for fname in os.listdir(folder):
                if fname.lower().endswith(".pdf"):
                    path = os.path.join(folder, fname)
                    try:
                        reader = PdfReader(path)
                        content = ""
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                content += text.lower()
                        if all(k in content for k in keywords):
                            results.append(fname)
                    except Exception as e:
                        print(f"Napaka pri branju {fname}: {e}")
    return render_template_string(HTML, results=results, folder=folder)


@app.route("/files/<path:folder>/<filename>")
def serve_file(folder, filename):
    return send_from_directory(folder, filename)


if __name__ == "__main__":
    app.run(debug=True)
