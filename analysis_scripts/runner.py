from analysis_scripts import geolocator, loc_finder, collector
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import spacy
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

nlp = spacy.load('en_core_web_sm')

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

def calculate_pmi(text, n=8):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    counter = Counter(tokens)
    bigram_counts = Counter(zip(tokens[:-1], tokens[1:]))
    total_words = len(tokens)
    pmi_scores = {bigram: pmi(bigram_counts[bigram], counter[bigram[0]], counter[bigram[1]], total_words) for bigram in bigram_counts}
    sorted_scores = sorted(pmi_scores.items(), key=lambda x: x[1], reverse=True)
    return [bigram[0] for bigram in sorted_scores[:n]]

# TEST
# def extract_phrases(text, n=10):
#     doc = nlp(text)
#     tokens = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
#     text_str = " ".join(tokens)
#     bigrams = calculate_pmi(text_str, n)
#     sorted_bigrams = sorted(bigrams, key=lambda x: x[1], reverse=True)[:n]
#     phrases = []
#     for bigram in sorted_bigrams:
#         phrase = " ".join(bigram[0].split("-"))
#         phrases.append(phrase)
#     return phrases

def pmi(bigram_count, word1_count, word2_count, total_words):
    p_bigram = bigram_count / total_words
    p_word1 = word1_count / total_words
    p_word2 = word2_count / total_words
    return round((pmi_helper(p_bigram, p_word1, p_word2) * total_words), 2)

def pmi_helper(p_bigram, p_word1, p_word2):
    return (p_bigram / (p_word1 * p_word2))

def run_and_get_single(url):
    article = collector.create_single_paper(url)

    # expensive right now because loc finder is also downloading
    # article_to_loc_map = loc_finder.get_locs([article])

    article.download()
    article.parse()
    text = article.text
    title = article.title
    summary = summarize(text, 0.2)


    # Load English tokenizer, tagger, parser and NER
    nlp = spacy.load("en_core_web_sm")

    # Process whole documents
    doc = nlp(text)

    # Find named entities, phrases and concepts
    loc_entities = []
    for entity in doc.ents:
        if entity.label_ == "GPE" or entity.label_ == "LOC":
            loc_entities.append(entity.text)



    if not loc_entities:
        return (title, summary, (0,0), "NO LOCATION FOUND", ["No Tags"])
    else:
        # select the loc that occurs the most often in the article
        # if there are multiple, select the first one
        # if there are none, select the first one
        # if there are none, return None
        loc = max(set(loc_entities), key=loc_entities.count)

        geocoder = Nominatim(user_agent='geolocator-news-analyzer')
        geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

        located_gpe = geolocator.get_locations([loc], geocode)[0][1]

        # find tags
        tags = calculate_pmi(text, 5)

        # clean the tags to combine the words in the tuple. also uppercase the first letter of each word if it's not a proper noun

        # tags = [tag[0] + " " + tag[1] for tag in tags]
        tags = [tag[0].title() + " " + tag[1].title() for tag in tags]

        print(tags)
        #
        # phrases = extract_phrases(text, 5)
        # print(phrases)

        return (title, summary, located_gpe, loc, tags)


# def textSummarizer(text, percentage):
#     # load the model into spaCy
#     nlp = spacy.load('en_core_web_sm')
#
#     # pass the text into the nlp function
#     doc = nlp(text)
#
#     ## The score of each word is kept in a frequency table
#     tokens = [token.text for token in doc]
#     freq_of_word = dict()
#
#     # Text cleaning and vectorization
#     for word in doc:
#         if word.text.lower() not in list(STOP_WORDS):
#             if word.text.lower() not in punctuation:
#                 if word.text not in freq_of_word.keys():
#                     freq_of_word[word.text] = 1
#                 else:
#                     freq_of_word[word.text] += 1
#
#     # Maximum frequency of word
#     if not freq_of_word.values():
#         return "NO TEXT IN ARTICLE FOUND and/or error in textSummarizer"
#     max_freq = max(freq_of_word.values())
#
#     # Normalization of word frequency
#     for word in freq_of_word.keys():
#         freq_of_word[word] = freq_of_word[word] / max_freq
#
#     # In this part, each sentence is weighed based on how often it contains the token.
#     sent_tokens = [sent for sent in doc.sents]
#     sent_scores = dict()
#     for sent in sent_tokens:
#         for word in sent:
#             if word.text.lower() in freq_of_word.keys():
#                 if sent not in sent_scores.keys():
#                     sent_scores[sent] = freq_of_word[word.text.lower()]
#                 else:
#                     sent_scores[sent] += freq_of_word[word.text.lower()]
#
#     len_tokens = int(len(sent_tokens) * percentage)
#
#     # Summary for the sentences with maximum score. Here, each sentence in the list is of spacy.span type
#     summary = nlargest(n=len_tokens, iterable=sent_scores, key=sent_scores.get)
#
#     # Prepare for final summary
#     final_summary = [word.text for word in summary]
#
#     # convert to a string
#     summary = " ".join(final_summary)
#
#     return summary
#     # Return final summary

def summarize(text, percent=0.2):
    doc = nlp(text)
    max_length_chars = int(len(text) * percent)
    sentences = [sent.text.strip() for sent in doc.sents]
    scores = []
    for i, sentence in enumerate(sentences):
        sent_doc = nlp(sentence)
        similarity_scores = [sent_doc.similarity(nlp(other_sent)) for other_sent in sentences if other_sent != sentence]
        if similarity_scores:
            similarity_score = sum(similarity_scores) / len(similarity_scores)
        else:
            similarity_score = 0
        scores.append((i, sentence, similarity_score))
    sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)
    summary = []
    length = 0
    for i, sentence, score in sorted_scores:
        if len(summary) + 1 <= len(sentences) * percent and length + len(sentence) <= max_length_chars:
            summary.append(sentence)
            length += len(sentence)
        else:
            break
    return " ".join(summary)

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
