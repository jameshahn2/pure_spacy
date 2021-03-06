import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy import displacy
from string import punctuation
from heapq import nlargest

nlp = spacy.load('en_core_web_sm')


def text_summarizer(raw_docx):
    rawtext = raw_docx
    docx = nlp(rawtext)
    stopwords = list(STOP_WORDS)
    # Build Word Frequency
    # word.text is tokenization in spacy
    word_frequencies = {}
    for word in docx:
        if word.text not in stopwords:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequency)
    # Sentence Tokens
    sentence_list = [sentence for sentence in docx.sents]
    # Sentence Scores
    sentence_scores = {}
    for sent in sentence_list:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]

    summarized_sentences = nlargest(6, sentence_scores, key=sentence_scores.get)
    final_sentences = [f'{w.text}' for w in summarized_sentences]
    return list(final_sentences)
    print("Original Document\n")
    print(raw_docx)
    print("Total Length:", len(raw_docx))
    print('\n\nSummarized Document\n')
    print(final_sentences)
    print("Total Length:", len(final_sentences))
