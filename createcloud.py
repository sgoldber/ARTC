from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import nltk
from nltk.collocations import *
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import sent_tokenize
import string
#import sys

# read the json data
json_data=open("data.json").read()
data = json.loads(json_data)

# sort reviews by author
sorted_list = sorted(data[0]["reviews"], key=lambda k: k['review_author'])
#print(len(sorted_list))
# remove reviews that are too similar
similar_removed = []
for i in range(len(sorted_list)):
	if i != 0:
		shared_items = set(sorted_list[i].items()) & set(sorted_list[i-1].items())
		if len(shared_items) < 4:
			similar_removed.append(sorted_list[i-1])
		#else:
			#print(sorted_list[i-1])
similar_removed.append(sorted_list[-1])

#print(len(similar_removed))
# write the sorted/cleaned json
#f=open('data_sorted.json','w')
#json.dump(data,f,indent=4)

#exit early
#sys.exit()

#pull out the review text and the titles for good and bad
text = ""
titles_good = ""
titles_bad = ""
for review in similar_removed:
	text += ' ' + review["review_text"]
	if float(review["review_rating"]) > 3.0:
		titles_good += '.' + review["review_header"]
	if float(review["review_rating"]) <= 3.0:
		titles_bad += '.' + review["review_header"]

# tokenize the review text and look for quadgrams
lowers = text.lower()
#remove the punctuation using the character deletion step of translate
no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
tknzr = TweetTokenizer()
tokens = tknzr.tokenize(no_punctuation)
finder = QuadgramCollocationFinder.from_words(tokens)
# only ngrams that appear 3+ times
finder.apply_freq_filter(3) 

# create output text with ngrams repeated according to their PMI value
#top_20 = []
output_text = ""
trigram_measures = nltk.collocations.TrigramAssocMeasures()
for ngram, pmi in finder.score_ngrams(trigram_measures.pmi)[:20]:
	content = ' '.join(ngram)
	#top_20.append(content)
	output_text = output_text + '|' + '|'.join([content[:]]*int(pmi))

#sent_tokenize_list = sent_tokenize(lowers)
#for ngram in top_20:
	#print ("NGRAM: " + ngram + "\n")
	#for sent in sent_tokenize_list:
		#if ngram in sent:
			#print(sent)

# Create Word Cloud for review text
wordcloud = WordCloud(max_font_size=40, regexp="[\w\s]+", collocations=False).generate(output_text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# Create word cloud for title text (good)
wordcloud = WordCloud(scale=.5, max_font_size=40, max_words=20, colormap="YlGn")
wc_output = wordcloud.generate(titles_good)
plt.figure()
plt.imshow(wc_output, interpolation="bilinear")
plt.axis("off")
plt.show()

# Create word cloud for title text (bad)
wordcloud = WordCloud(width=200, height=100, max_font_size=40, max_words=20, colormap="OrRd").generate(titles_bad)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
