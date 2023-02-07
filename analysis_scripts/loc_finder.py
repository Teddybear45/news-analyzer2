import spacy
def get_locs(articles):
    article_to_loc_map = {}
    nlp = spacy.load("en_core_web_sm")
    for article in articles:
        article.download()
        article.parse()
        article_text = article.text

        doc = nlp(article_text)

        loc_set = set()
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE']:
                loc_set.add(ent.text)

        if loc_set:
            article_to_loc_map[article.url] = loc_set

    return article_to_loc_map
