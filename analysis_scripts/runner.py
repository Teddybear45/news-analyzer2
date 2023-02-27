from analysis_scripts import geolocator, loc_finder, collector
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest


# {url: [(city, (lat, long)), ...],...}
def run_and_get_geolocs():
    articles = collector.get_newspaper_articles()[0:5]

    article_to_loc_map = loc_finder.get_locs(articles)

    geocoder = Nominatim(user_agent='geolocator-news-analyzer')
    geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

    article_to_geoloc_map = {}

    for url in article_to_loc_map.keys():
        gpes = article_to_loc_map[url]
        located_gpes = geolocator.get_locations(gpes, geocode)

        article_to_geoloc_map[url] = located_gpes

    return article_to_geoloc_map


def run_and_get_single(url):
    article = collector.create_single_paper(url)

    # expensive right now because loc finder is also downloading
    # article_to_loc_map = loc_finder.get_locs([article])

    article.download()
    article.parse()
    text = article.text
    print(text)

    # Load English tokenizer, tagger, parser and NER
    nlp = spacy.load("en_core_web_sm")

    # Process whole documents
    doc = nlp(text)

    # Find named entities, phrases and concepts
    loc_entities = []
    for entity in doc.ents:
        if entity.label_ == "GPE" or entity.label_ == "LOC":
            loc_entities.append(entity.text)

    # select the loc that occurs the most often in the article
    # if there are multiple, select the first one
    # if there are none, select the first one
    # if there are none, return None
    if not loc_entities:
        return "NO LOCATIONS FOUND IN ARTICLE"
    else:
        loc = max(set(loc_entities), key=loc_entities.count)

    geocoder = Nominatim(user_agent='geolocator-news-analyzer')
    geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

    located_gpe = geolocator.get_locations([loc], geocode)[0][1]

    summary = textSummarizer(text, 0.5)

    return (summary, located_gpe, loc)


def textSummarizer(text, percentage):
    # load the model into spaCy
    nlp = spacy.load('en_core_web_sm')

    # pass the text into the nlp function
    doc = nlp(text)

    ## The score of each word is kept in a frequency table
    tokens = [token.text for token in doc]
    freq_of_word = dict()

    # Text cleaning and vectorization
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in freq_of_word.keys():
                    freq_of_word[word.text] = 1
                else:
                    freq_of_word[word.text] += 1

    # Maximum frequency of word
    if not freq_of_word.values():
        return "NO TEXT IN ARTICLE FOUND and/or error in textSummarizer"
    max_freq = max(freq_of_word.values())

    # Normalization of word frequency
    for word in freq_of_word.keys():
        freq_of_word[word] = freq_of_word[word] / max_freq

    # In this part, each sentence is weighed based on how often it contains the token.
    sent_tokens = [sent for sent in doc.sents]
    sent_scores = dict()
    for sent in sent_tokens:
        for word in sent:
            if word.text.lower() in freq_of_word.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = freq_of_word[word.text.lower()]
                else:
                    sent_scores[sent] += freq_of_word[word.text.lower()]

    len_tokens = int(len(sent_tokens) * percentage)

    # Summary for the sentences with maximum score. Here, each sentence in the list is of spacy.span type
    summary = nlargest(n=len_tokens, iterable=sent_scores, key=sent_scores.get)

    # Prepare for final summary
    final_summary = [word.text for word in summary]

    # convert to a string
    summary = " ".join(final_summary)

    # Return final summary
    return summary


if __name__ == '__main__':
    articles = collector.get_newspaper_articles()[0:5]

    article_to_loc_map = loc_finder.get_locs(articles)

    geocoder = Nominatim(user_agent='geolocator-news-analyzer')
    geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

    article_to_geoloc_map = {}

    for url in article_to_loc_map.keys():
        gpes = article_to_loc_map[url]
        located_gpes = geolocator.get_locations(gpes, geocode)

        article_to_geoloc_map[url] = located_gpes

    print(article_to_geoloc_map)
