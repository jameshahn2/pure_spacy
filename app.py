from __future__ import unicode_literals
from bs4 import BeautifulSoup, SoupStrainer
from flask import Flask, render_template, url_for, request
from gensim.summarization import summarize
from nltk_summarization import nltk_summarizer
from spacy_summarization import text_summarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from spacy.lang.en import English
import flask
import requests
import spacy
import spacy_summarization
import time

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


# Sumy
def sumy_summary(doc):
    parser = PlaintextParser.from_string(doc, Tokenizer("english"))
    lex_summarizer = LexRankSummarizer()
    summary = lex_summarizer(parser.document, 3)
    summary_list = [str(sentence) for sentence in summary]
    result = ' '.join(summary_list)
    return result


# Reading Time
def readingtime(mytext):
    total_words = len([token.text for token in nlp(mytext)])
    estimatedTime = total_words / 200.0
    return estimatedTime


# Get page from URL
def get_page(page_url, retry=0):
    try:
        response = requests.get(page_url, headers=headers, timeout=30)
        return response.content
    except:
        if retry < 5:
            return getPage(page_url, retry=retry + 1)
        else:
            return 0


# Fetch Text From Url
def get_text(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()  # rip it out
    fetched_text = ' '.join(
        map(lambda p: p.text, soup.select('.content-text.content-text-article,.l-container,'
                                          '.entry-content.entry-content-read-more,.asset-content.p402_premium.subscriber-premium,'
                                          '.bigtext,.entry-content,.HomeTopRow.ContentFullWidth.home_slideshow.section_feature.google_standout.section_follow_1.section_follow_2.section_follow_3,'
                                          '.c-article__body.o-rte-text.u-spacing.l-container--content.ember-view,'
                                          '.body-text,.entry-content.Entry-content,.article-body,.story-body,.body-content,'
                                          '.article-content.rich-text,.article-content-wrapper,.postBody,.td-post-content,.m-entry-content,'
                                          'section.c-main__body.js-original-content-body.s-content,.p402_premium,.content-copy')))
    return fetched_text


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    global summary_reading_time_nltk
    start = time.time()
    if flask.request.method == 'POST':
        rawtext = flask.request.form['rawtext']
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(final_summary_spacy)
        # Gensim Summarizer
        final_summary_gensim = summarize(rawtext)
        summary_reading_time_gensim = readingtime(final_summary_gensim)
        # NLTK
        final_summary_nltk = nltk_summarizer(rawtext)
        summary_reading_time_nltk = readingtime(final_summary_nltk)
        # Sumy
        final_summary_sumy = sumy_summary(rawtext)
        summary_reading_time_sumy = readingtime(final_summary_sumy)

        end = time.time()
        final_time = end - start
    return flask.render_template('index.html', ctext=rawtext, final_summary_spacy=final_summary_spacy,
                                 final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                                 final_time=final_time, final_reading_time=final_reading_time,
                                 summary_reading_time=summary_reading_time,
                                 summary_reading_time_gensim=summary_reading_time_gensim,
                                 final_summary_sumy=final_summary_sumy,
                                 summary_reading_time_sumy=summary_reading_time_sumy,
                                 summary_reading_time_nltk=summary_reading_time_nltk)


@app.route('/analyze_url', methods=['GET', 'POST'])
def analyze_url():
    start: float = time.time()
    if request.method == 'POST':
        raw_url = request.form['raw_url']
        rawtext: str = get_text(raw_url)
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(final_summary_spacy)
        # Gensim Summarizer
        final_summary_gensim = summarize(rawtext)
        summary_reading_time_gensim = readingtime(final_summary_gensim)
        # NLTK
        final_summary_nltk = nltk_summarizer(rawtext)
        summary_reading_time_nltk = readingtime(final_summary_nltk)
        # Sumy
        final_summary_sumy = sumy_summary(rawtext)
        summary_reading_time_sumy = readingtime(final_summary_sumy)

        end = time.time()
        final_time = end - start
    return flask.render_template('index.html', ctext=rawtext, final_summary_spacy=final_summary_spacy,
                                 final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                                 final_time=final_time, final_reading_time=final_reading_time,
                                 summary_reading_time=summary_reading_time,
                                 summary_reading_time_gensim=summary_reading_time_gensim,
                                 final_summary_sumy=final_summary_sumy,
                                 summary_reading_time_sumy=summary_reading_time_sumy,
                                 summary_reading_time_nltk=summary_reading_time_nltk)


@app.route('/about')
def about():
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
