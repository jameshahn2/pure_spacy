from __future__ import unicode_literals
from flask import Flask, render_template, url_for, request
from flaskext.markdown import Markdown
from gensim.summarization import summarize
from newspaper import Article, fulltext
from nltk_summarization import nltk_summarizer
from nltk.tokenize import sent_tokenize
from spacy import displacy
from spacy.pipeline import EntityRuler, merge_entities, merge_noun_chunks
from spacy_summarization import text_summarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from spacy.lang.en import English
import csv
import pandas as pd
import spacy
import spacy_summarization
import time
import flaskext
import flask
import json
import requests

headers = {
    'authority': 'triberocket.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/78.0.3904.108 Safari/537.36',
    'sec-fetch-user': '?1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9'
}

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
Markdown(app)

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""


# Sumy
def sumy_summary(docx):
    parser = PlaintextParser.from_string(docx, Tokenizer("english"))
    lex_summarizer = LexRankSummarizer()
    summary = lex_summarizer(parser.document, 5)
    result = [str(sentence) for sentence in summary]
    return list(result)


# Reading Time
def readingtime(mytext):
    total_words = len([token.text for token in nlp(mytext)])
    estimatedTime = total_words / 200.0
    return estimatedTime


# Fetch Text From Url
def get_text(url):
    r = requests.get(url, headers=headers, timeout=30).text
    article = Article(url)
    article.download()
    article.parse()
    return article.text


@app.route('/')
def index():
    # rawtext = "Bill Gates is An American Computer Scientist since 1986"
    # doc = nlp(rawtext)
    # html = displacy.render(doc,style="ent")
    # html = html.replace("\n\n","\n")
    # result = HTML_WRAPPER.format(html)

    return flask.render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    start = time.time()
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(str(final_summary_spacy))
        docx = nlp(rawtext)
        html = displacy.render(docx, style='ent')
        html = html.replace("\n\n", "\n")
        entity_result = HTML_WRAPPER.format(html)
        pos_results = [(token.text, token.pos_, token.shape_, token.dep_) for token in docx]
        df = pd.DataFrame(pos_results, columns=['Word', 'Parts of Speech', 'Word Shape', 'Dependency'])
        # Gensim Summarizer
        final_summary_gensim = summarize(rawtext, split=True)
        summary_reading_time_gensim = readingtime(str(final_summary_gensim))
        # NLTK
        final_summary_nltk = nltk_summarizer(rawtext)
        summary_reading_time_nltk = readingtime(str(final_summary_nltk))
        # Sumy
        final_summary_sumy = sumy_summary(rawtext)
        summary_reading_time_sumy = readingtime(str(final_summary_sumy))

        end = time.time()
        final_time = end - start

        # Word Stats
        tokens_results = [token.text for token in docx]
        entity_list = [(entity.text, entity.label_) for entity in docx.ents]
        lemma_list = [token.lemma_ for token in docx]
        adj_list = [token for token in docx if token.pos_ == 'ADJ']
        noun_list = [token for token in docx if token.pos_ == 'NOUN']
    return render_template('summaries.html', ctext=rawtext, entity_result=entity_result, dftable=df, adj_list=adj_list,
                           entity_list=entity_list,
                           final_reading_time=final_reading_time,
                           final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                           final_summary_spacy=final_summary_spacy,
                           final_summary_sumy=final_summary_sumy, final_time=final_time,
                           lemma_list=lemma_list, noun_list=noun_list, summary_reading_time=summary_reading_time,
                           summary_reading_time_gensim=summary_reading_time_gensim,
                           summary_reading_time_nltk=summary_reading_time_nltk,
                           summary_reading_time_sumy=summary_reading_time_sumy, tokens_results=tokens_results)


@app.route('/analyze_url', methods=['GET', 'POST'])
def analyze_url():
    start = time.time()
    if request.method == 'POST':
        raw_url = request.form['raw_url']
        rawtext = get_text(raw_url)
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_4_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(str(final_summary_spacy))
        docx = nlp(rawtext)
        html = displacy.render(docx, style='ent')
        html = html.replace("\n\n", "\n")
        entity_result = HTML_WRAPPER.format(html)
        pos_results = [(token.text, token.pos_, token.shape_, token.dep_) for token in docx]
        df = pd.DataFrame(pos_results, columns=['Word', 'Parts of Speech', 'Word Shape', 'Dependency'])
        # Gensim Summarizer
        final_summary_gensim = summarize(rawtext, split=True)
        summary_reading_time_gensim = readingtime(str(final_summary_gensim))
        # NLTK
        final_summary_nltk = nltk_summarizer(rawtext)
        summary_reading_time_nltk = readingtime(str(final_summary_nltk))
        # Sumy
        final_summary_sumy = sumy_summary(rawtext)
        summary_reading_time_sumy = readingtime(str(final_summary_sumy))

        with open('sumitup.csv', 'w', newline='') as f:
            writecsv = csv.writer(f)

            writecsv.writerow(['spaCy', 'Gensim', 'NLTK', 'Sumy'])
            writecsv.writerow([(final_summary_spacy), (final_summary_gensim), (final_summary_nltk), (final_summary_sumy)])

        end = time.time()
        final_time = end - start

        # Word Stats
        tokens_results = [token.text for token in docx]
        entity_list = [(entity.text, entity.label_) for entity in docx.ents]
        lemma_list = [token.lemma_ for token in docx]
        adj_list = [token for token in docx if token.pos_ == 'ADJ']
        noun_list = [token for token in docx if token.pos_ == 'NOUN']
    return render_template('summaries.html', ctext=rawtext, entity_result=entity_result, dftable=df, adj_list=adj_list,
                           entity_list=entity_list,
                           final_reading_time=final_reading_time,
                           final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                           final_summary_spacy=final_summary_spacy,
                           final_summary_sumy=final_summary_sumy, final_time=final_time,
                           lemma_list=lemma_list, noun_list=noun_list, summary_reading_time=summary_reading_time,
                           summary_reading_time_gensim=summary_reading_time_gensim,
                           summary_reading_time_nltk=summary_reading_time_nltk,
                           summary_reading_time_sumy=summary_reading_time_sumy, tokens_results=tokens_results)


@app.route('/summaries', methods=['GET', 'POST'])
def summaries():
    start = time.time()
    if request.method == 'POST':
        raw_url = request.form['raw_url']
        rawtext = get_text(raw_url)
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(str(final_summary_spacy))
        docx = nlp(rawtext)
        html = displacy.render(docx, style='ent')
        html = html.replace("\n\n", "\n")
        entity_result = HTML_WRAPPER.format(html)
        pos_results = [(token.text, token.pos_, token.shape_, token.dep_) for token in docx]
        df = pd.DataFrame(pos_results, columns=['Word', 'Parts of Speech', 'Word Shape', 'Dependency'])
        # Gensim Summarizer
        final_summary_gensim = summarize(rawtext, split=True)
        summary_reading_time_gensim = readingtime(str(final_summary_gensim))
        # NLTK
        final_summary_nltk = nltk_summarizer(rawtext)
        summary_reading_time_nltk = readingtime(str(final_summary_nltk))
        # Sumy
        final_summary_sumy = sumy_summary(rawtext)
        summary_reading_time_sumy = readingtime(str(final_summary_sumy))
        # Final Summary
        final_summary = summarize(nltk_summarizer(text_summarizer(sumy_summary)))

        end = time.time()
        final_time = end - start
    return render_template('summaries.html', ctext=rawtext, entity_result=entity_result, dftable=df, adj_list=adj_list,
                           entity_list=entity_list,
                           final_reading_time=final_reading_time,
                           final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                           final_summary_spacy=final_summary_spacy,
                           final_summary_sumy=final_summary_sumy, final_time=final_time,
                           lemma_list=lemma_list, noun_list=noun_list, summary_reading_time=summary_reading_time,
                           summary_reading_time_gensim=summary_reading_time_gensim,
                           summary_reading_time_nltk=summary_reading_time_nltk,
                           summary_reading_time_sumy=summary_reading_time_sumy, tokens_results=tokens_results,
                           summary_4_spacy=summary_4_spacy, summary_4_gensim=summary_4_gensim, summary_4_nltk=summary_4_nltk,
                           summary_4_sumy=summary_4_sumy, final_summary=final_summary)


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


if __name__ == "__main__":
    app.run(debug=True)

