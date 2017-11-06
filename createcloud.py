from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import nltk
from nltk.collocations import *
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import sent_tokenize
import string

#bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

json_data=open("data.json").read()

data = json.loads(json_data)
text = ""
titles_good = ""
titles_bad = ""
for review in data[0]["reviews"]:
	if float(review["review_rating"]) > 3.0:
		text += review["review_text"]
		titles_good += review["review_header"]
	if float(review["review_rating"]) <= 3.0:
		titles_bad += review["review_header"]

# testing sorting and filtering
#data[0]["reviews"] = sorted(data[0]["reviews"], key=lambda k: k['review_author']) 
#with open('data_sorted.json', 'w') as f:
  #json.dump(data, f, ensure_ascii=False)

# tokenize and look for quadgrams
lowers = text.lower()
#remove the punctuation using the character deletion step of translate
no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
tknzr = TweetTokenizer()
tokens = tknzr.tokenize(no_punctuation)
finder = QuadgramCollocationFinder.from_words(tokens)
# only bigrams that appear 3+ times
finder.apply_freq_filter(3) 

# create output text with ngrams repeated according to their PMI value
top_20 = []
output_text = ""
for ngram, pmi in finder.score_ngrams(trigram_measures.pmi)[:20]:
	content = ' '.join(ngram)
	top_20.append(content)
	output_text = output_text + '|' + '|'.join([content[:]]*int(pmi))

sent_tokenize_list = sent_tokenize(lowers)
for ngram in top_20:
	print ("NGRAM: " + ngram + "\n")
	for sent in sent_tokenize_list:
		if ngram in sent:
			print(sent)

# Create Word Cloud for review text
#wordcloud = WordCloud(max_font_size=40, regexp="[\w\s]+", collocations=False).generate(output_text)
#plt.figure()
#plt.imshow(wordcloud, interpolation="bilinear")
#plt.axis("off")
#plt.show()

# Create word cloud for title text
wordcloud = WordCloud(max_font_size=40).generate(titles_good)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

wordcloud = WordCloud(max_font_size=40).generate(titles_bad)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
