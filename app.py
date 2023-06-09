from flask import Flask, request, render_template
from flask import jsonify

app = Flask(__name__)

from analysis_scripts import runner
from analysis_scripts import collector
import rerender


@app.route("/")
def main_page():
    # article_loc_map = runner.run_and_get_geolocs()
    # return "<div><p>Hello, World!</p><p>{}</p></div>".format(articles_urls)
    # , locData="jsonify(article_loc_map)"

    articles = collector.get_newspaper_articles()
    print(articles)
    for a in articles:
        print(a.title)

    return render_template('index.html', articles=articles)

@app.route("/", methods=['POST'])
def main_page_post():
    url = request.form['url']
    res = runner.run_and_get_single(url)

    title = res[0]
    summary = res[1]
    coords = res[2]
    loc = res[3]
    tags = res[4]

    return render_template('single.html', title=title, summary=summary, lon=coords[1], lat=coords[0], loc=loc, tags=tags)


# @app.route("/old_single_select")
# def single_select():
#     url = "https://www.cnn.com/2023/02/25/weather/winter-storm-us-saturday/index.html"
#     res = runner.run_and_get_single(url)
#
#     return render_template('single.html', entities=res[0], summary=res[1])



@app.route("/api/analyze_all")
def analyze_all():
    article_loc_map = runner.run_and_get_geolocs()
    rerender.render_and_save_map(article_loc_map)


@app.route("/api/rerender")
def rerender_all():
    article_loc_map = runner.run_and_get_geolocs()
    rerender.render_and_save_map(article_loc_map)



@app.route("/render_map")
def rendered():
    return render_template('renderAll.html')