# produces a DataFrame of comparative word frequencies from a natural language texts.
#
# First step in TF / IDF analysis.
# http://en.wikipedia.org/wiki/Tf%E2%80%93idf
#
# --@nthmost 2/22/2014

import os
import pandas as pd

PUNC=set("()$!,./;'?&\'\":")

CORP_DIR = './corpora/'

f = open('frequent_words_less.txt', 'r')
MOST_FREQUENT_WORDS = f.read().split('\n')

def word_count(text_data, ignore_words=MOST_FREQUENT_WORDS, punc=PUNC):
    '''
    text_data - list of strings
    wordFreq  - list with frequent words to exlude
    punc      - string with punctuation to exclude
    '''
    words={}

    for line in text_data:
        for ww in line.split():
            word = ww.lower()
            word = ''.join((x for x in word if x not in punc))
        
            if word not in ignore_words:
                if words.has_key(word):
                    words[word] += 1
                else:
                    words[word] = 1
    return words


if __name__=='__main__':

    corpora = {}
    for filename in os.listdir(CORP_DIR):
        lines = open(os.path.join(CORP_DIR, filename), 'r').readlines()
        corpora[filename] = word_count(lines)

    df = pd.DataFrame(corpora)

    print df

