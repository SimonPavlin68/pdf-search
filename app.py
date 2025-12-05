from flask import Flask, render_template_string, request, send_from_directory
import os
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Iskanje PDF-jev</title>
<h2>📂 Lokalni PDF-ji</h2>
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

<hr>
<h2>🌐 PDF-ji s spletne strani</h2>
<form method="POST">
    URL spletne strani: 
    <input type="text" name="web_url" size="70" value="{{ web_url }}"><br><br>
    <input type="submit" value="Pridobi PDF-je">
</form>

<div id="web_results">
{% if pdf_links is not none %}
    {% if pdf_links %}
        <p>Najdeni PDF-ji na strani "{{ web_url }}":</p>
        <ul>
        {% for link in pdf_links %}
            <li><a href="{{ link }}" target="_blank">{{ link }}</a></li>
        {% endfor %}
        </ul>
        <p>Število najdenih dokumentov: {{ pdf_links|length }}</p>
    {% else %}
        <p>Na strani ni PDF-jev.</p>
    {% endif %}
{% endif %}
</div>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    # Lokalni PDF-ji
    results = None
    # folder = "D:\\simon\\lok\\LZS\\io\\stari zapisniki"
    folder = "pdf"
    keywords = ""

    # Spletni PDF-ji
    pdf_links = None
    web_url = "https://www.archery-si.org/organi/"

    if request.method == "POST":
        # Če je vnos lokalnih PDF-jev
        if "folder" in request.form and "keywords" in request.form:
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

        # Če je vnos URL spletne strani
        if "web_url" in request.form:
            web_url = request.form["web_url"]
            pdf_links = []
            if web_url:
                try:
                    resp = requests.get(web_url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.lower().endswith('.pdf'):
                            full_url = urljoin(web_url, href)
                            pdf_links.append(full_url)
                except Exception as e:
                    print(f"Napaka pri branju spletne strani {web_url}: {e}")

    return render_template_string(
        HTML,
        results=results, folder=folder, keywords=keywords,
        pdf_links=pdf_links, web_url=web_url
    )


@app.route("/files/<path:folder>/<filename>")
def serve_file(folder, filename):
    return send_from_directory(folder, filename)


if __name__ == "__main__":
    app.run(debug=True)
