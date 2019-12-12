from __future__ import unicode_literals
from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request
from flaskext.markdown import Markdown
from gensim.summarization import summarize
from nltk_summarization import nltk_summarizer
from newspaper import Article, fulltext
from spacy import displacy
from spacy_summarization import text_summarizer
from sumy.nlp.tokenizers import Tokenizer
from nltk.tokenize import sent_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from spacy.lang.en import English
import flask
import json
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
Markdown(app)

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""


# Sumy
def sumy_summary(doc):
    parser = PlaintextParser.from_string(doc, Tokenizer("english"))
    lex_summarizer = LexRankSummarizer()
    summary = lex_summarizer(parser.document, 5)
    result = [str(sentence) for sentence in summary]
    return list(result)


# Reading Time
def readingtime(mytext):
    total_words = len([token.text for token in nlp(mytext)])
    estimatedTime = total_words / 200.0
    return estimatedTime


@app.route('/')
def index():
    # raw_text = "Bill Gates is An American Computer Scientist since 1986"
    # doc = nlp(rawtext)
    # html = displacy.render(doc,style="ent")
    # html = html.replace("\n\n","\n")
    # result = HTML_WRAPPER.format(html)

    return flask.render_template('index.html')


@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == 'POST':
        raw_text = request.form['rawtext']
        docx = nlp(raw_text)
        html = displacy.render(docx, style="ent")
        html = html.replace("\n\n", "\n")
        result = HTML_WRAPPER.format(html)

    return render_template('result.html', rawtext=raw_text, result=result)


@app.route('/previewer')
def previewer():
    return render_template('previewer.html')


@app.route('/preview', methods=["GET", "POST"])
def preview():
    if request.method == 'POST':
        newtext = request.form['newtext']
        result = newtext

    return render_template('preview.html', newtext=newtext, result=result)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    global summary_reading_time_nltk
    start = time.time()
    if flask.request.method == 'POST':
        rawtext = flask.request.form['rawtext']
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(str(final_summary_spacy))
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
    return render_template('analyze_url.html', ctext=rawtext, final_summary_spacy=final_summary_spacy,
                           final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                           final_time=final_time, final_reading_time=final_reading_time,
                           summary_reading_time=summary_reading_time,
                           summary_reading_time_gensim=summary_reading_time_gensim,
                           final_summary_sumy=final_summary_sumy,
                           summary_reading_time_sumy=summary_reading_time_sumy,
                           summary_reading_time_nltk=summary_reading_time_nltk)


# Fetch Text From Url
def get_text(url):
    r = requests.get(url, headers=headers, timeout=30).text
    article = Article(url)
    article.download()
    print(article.text)
    article.parse()
    return article.text


@app.route('/analyze_url', methods=['GET', 'POST'])
def analyze_url():
    start = time.time()
    if request.method == 'POST':
        raw_url = request.form['raw_url']
        rawtext = get_text(raw_url)
        final_reading_time = readingtime(rawtext)
        final_summary_spacy = text_summarizer(rawtext)
        summary_reading_time = readingtime(str(final_summary_spacy))
        final_summary_spacy_str = str(final_summary_spacy)
        print(final_summary_spacy)
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
    return render_template('analyze_url.html', ctext=rawtext, final_summary_spacy=final_summary_spacy,
                           final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk,
                           final_time=final_time, final_reading_time=final_reading_time,
                           summary_reading_time=summary_reading_time,
                           summary_reading_time_gensim=summary_reading_time_gensim,
                           final_summary_sumy=final_summary_sumy,
                           summary_reading_time_sumy=summary_reading_time_sumy,
                           summary_reading_time_nltk=summary_reading_time_nltk)


@app.route('/about')
def about():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
