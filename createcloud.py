from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import nltk
from nltk.collocations import *
from nltk.tokenize import TweetTokenizer
#from nltk.tokenize import PunktWordTokenizer
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

output_text = ""
# return the 10 n-grams with the highest PMI
#print(trigram_measures.pmi)
#for entry in finder.nbest(trigram_measures.pmi, 20):
index = 0
for entry in finder.score_ngrams(trigram_measures.pmi):
	content = ""
	for word in entry[0]:
		if (content == ""):
			content = word
		else:
			content = content + " " + word
	for i in range(int(entry[1])):
		output_text = output_text + "|" + content
	index += 1
	if index == 20:
		break;	
	#print(content)
	#print(entry[1])
	#output_text = output_text + "|" + content
#print(output_text)
wordcloud = WordCloud(max_font_size=40, regexp="[\w\s]+", collocations=False).generate(output_text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
