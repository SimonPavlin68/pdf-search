from flask import Flask, render_template_string, request, send_from_directory
import os
from pypdf import PdfReader

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Iskanje v PDF-jih</title>
<h2>Iskanje po PDF-jih</h2>
<form method="POST">
    Pot do direktorija: 
    <input type="text" name="folder" size="50" value="{{ folder }}"><br><br>
    Iskalne besede (ločene z vejico): 
    <input type="text" name="keywords" size="50" value="{{ keywords }}"><br><br>
    <input type="submit" value="Išči">
</form>

<div id="results">
{% if results is not none %}
    {% if results %}
        <p>Našel sem niz "{{ keywords }}" v {{ results|length }} dokumentih.</p>
        <ul>
        {% for pdf in results %}
            <li><a href="{{ url_for('serve_file', folder=folder, filename=pdf) }}" target="_blank">{{ pdf }}</a></li>
        {% endfor %}
        </ul>
    {% else %}
        <p>Ni dokumentov z ujemanjem za niz "{{ keywords }}".</p>
    {% endif %}
{% endif %}
</div>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    folder = "D:\\simon\\lok\\LZS\\io\\stari zapisniki"  # privzeta pot
    keywords = ""
    if request.method == "POST":
        folder = request.form["folder"]
        keywords = request.form["keywords"]
        keywords_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        results = []
        if os.path.isdir(folder) and keywords_list:
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
                        if all(k in content for k in keywords_list):
                            results.append(fname)
                    except Exception as e:
                        print(f"Napaka pri branju {fname}: {e}")
    return render_template_string(HTML, results=results, folder=folder, keywords=keywords)


@app.route("/files/<path:folder>/<filename>")
def serve_file(folder, filename):
    return send_from_directory(folder, filename)


if __name__ == "__main__":
    app.run(debug=True)
