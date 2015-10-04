#!/usr/bin/python3
"""
This script suggests lucene queries based on bigram collocations in a sample tweet file
"""
import nltk, argparse, re, json
from nltk.collocations import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# not a robust RE but will probably work fine here
link_re = re.compile(r"http[s]*://.*?($|\s)")
p_re = re.compile(r"[!.?;,]")

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Generate lucene queries from collocation data in a sample file")
    parser.add_argument("input",  help="File containing text corpus.")
    parser.add_argument("output", help="An output file.")
    parser.add_argument("-n","--number", default=100, help="Size of nbest list.")
    args = parser.parse_args()

    # extraction
    count=0
    docs = []
    mystopwords = stopwords.words("english")
    mystopwords.extend(['rt'])
    with open(args.input, "rb") as f:
        for l in f:
            count+=1
            try:
                tweet = json.loads(l.decode("utf-8").strip())
            except ValueError:
                print("Bad tweet found at line {0}.".format(count))
                tweet = {}

            if tweet.get("text"):
                tweet = tweet["text"]
                tweet = tweet.lower()
                tweet = re.sub(link_re, "", tweet).strip().replace("\"","")
                tweet = re.sub(p_re, "", tweet)
                # generally, word-tokenizer expects one sentance inputs.  Tweets might not satisfy that..but probably
                # doesn't matter for what we are doing here.
                tokens = [t.replace("'","") for t in tweet.split() if t not in mystopwords]
                docs.append(tokens)
            
    # get the nbest list
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_documents(docs)
    finder.apply_freq_filter(5)
    nbest = finder.nbest(bigram_measures.raw_freq, int(args.number))

    # create a file of queries
    #for k,v in finder.ngram_fd.items():
    #    print(k,v)

    with open(args.output, "w") as f:
        for q in nbest:
            query = { "type":"terms-query", "terms":list(q), "minimum-match":len(q) }
            f.write(json.dumps(query) + "\n")
