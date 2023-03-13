import datetime

import newspaper
from newspaper import news_pool, Config, Article
import time


paper_list = [
    # 'https://cnn.com',  # CNN / Separate finder
    # 'https://www.wsj.com/',  # WSJ // Not extracting
    # 'https://www.cbsnews.com/news/',  # CBS
    'https://apnews.com/',  # AP
    # 'https://www.nytimes.com/',  # NYT
    # 'https://www.washingtonpost.com/',  # WP
    # 'https://www.bbc.com/news',  # BBC
    # 'https://abcnews.go.com/',  # ABC
    # 'https://www.theatlantic.com/',  # The Atlantic
    # 'https://www.nbcnews.com/latest-stories',  # NBC
    # 'https://www.usatoday.com/',  # USA Today
    # 'https://www.theguardian.com/us',  # The Guardian
    # 'https://time.com/',  # TIME
    # 'https://www.npr.org/',  # NPR
]

def get_config():
    config = Config()
    config.memoize_articles = False
    config.request_timeout = 10
    config.keep_article_html = True
    config.fetch_images = False
    config.verbose = False
    config.language = 'en'
    config.MIN_WORD_COUNT = 400
    return config

def get_newspaper_articles():
    # articles = [newspaper.build(paper, config=get_config()).articles for paper in paper_list]
    paper = newspaper.build("https://apnews.com", config=get_config())
    articles = paper.articles
    return articles

def create_single_paper(url):
    article = Article(url)
    return article