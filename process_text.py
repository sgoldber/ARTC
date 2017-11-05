import nltk
from nltk.collocations import *
from nltk.tokenize import TweetTokenizer
#from nltk.tokenize import PunktWordTokenizer
import json
import string

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
#print(dir(nltk.tokenize))

json_data=open("data.json").read()

data = json.loads(json_data)
text = ""
for review in data[0]["reviews"]:
	if float(review["review_rating"]) >= 0.0:
		#print(".")
		text = text + review["review_text"]
	#else:
		#print("-")
#tokens = nltk.wordpunct_tokenize(text)

lowers = text.lower()
#remove the punctuation using the character deletion step of translate
no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
tknzr = TweetTokenizer()
tokens = tknzr.tokenize(no_punctuation)
finder = QuadgramCollocationFinder.from_words(tokens)

# change this to read in your data
#finder = BigramCollocationFinder.from_words(
#   nltk.corpus.genesis.words('english-web.txt'))

# only bigrams that appear 3+ times
finder.apply_freq_filter(3) 

# return the 10 n-grams with the highest PMI
for entry in finder.nbest(trigram_measures.pmi, 20):
	content = ""
	for word in entry:
		if (content == ""):
			content = word
		else:
			content = content + " " + word
	print(content)