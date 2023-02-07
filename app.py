from flask import Flask
from flask import render_template
from flask import jsonify

app = Flask(__name__)

from analysis_scripts import runner


@app.route("/")
def main():
    # article_loc_map = runner.run_and_get_geolocs()
    # return "<div><p>Hello, World!</p><p>{}</p></div>".format(articles_urls)
    return render_template('index.html', locData="jsonify(article_loc_map)")

@app.route("/api/analyze_all")
def analyze_all():
    article_loc_map = runner.run_and_get_geolocs()


@app.route("/render")
def rendered():
    return render_template('render.html')