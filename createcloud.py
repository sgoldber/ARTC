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
for review in data[0]["reviews"]:
	if float(review["review_rating"]) >= 0.0:
		text += review["review_text"]

# testing sorting and filtering
data[0]["reviews"] = sorted(data[0]["reviews"], key=lambda k: k['review_author']) 
with open('data_sorted.json', 'w') as f:
  json.dump(data, f, ensure_ascii=False)

lowers = text.lower()
#remove the punctuation using the character deletion step of translate
no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
tknzr = TweetTokenizer()
tokens = tknzr.tokenize(no_punctuation)
finder = QuadgramCollocationFinder.from_words(tokens)
# only bigrams that appear 3+ times
finder.apply_freq_filter(3) 

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

#wordcloud = WordCloud(max_font_size=40, regexp="[\w\s]+", collocations=False).generate(output_text)
#plt.figure()
#plt.imshow(wordcloud, interpolation="bilinear")
#plt.axis("off")
#plt.show()
