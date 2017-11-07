
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/		
import json, requests, re, sys, getopt, nltk, string, matplotlib.pyplot as plt
from dateutil import parser as dateparser
from time import sleep
from wordcloud import WordCloud
from lxml import html 
from nltk.collocations import *
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import sent_tokenize

def GetParser(url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(url,headers = headers)
	return(html.fromstring(page.text))

def FindAllReviews(asin):
	amazon_url = 'http://www.amazon.com/dp/'+asin
	parser = GetParser(amazon_url)

	XPATH_ALL_REVIEWS = '//a[@id="dp-summary-see-all-reviews"]//@href'
	all_reviews = parser.xpath(XPATH_ALL_REVIEWS)

	XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_ourprice"]/text()'
	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	product_price = ''.join(raw_product_price).replace(',','')

	XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'	
	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).strip()

	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
	ratings_dict = {}
	#grabing the rating section in product page
	for ratings in total_ratings:
		extracted_rating = ratings.xpath('./td//a//text()')
		if extracted_rating:
			rating_key = extracted_rating[0] 
			raw_raing_value = extracted_rating[1]
			rating_value = raw_raing_value
			if rating_key:
				ratings_dict.update({rating_key:rating_value})

	print('Reading Reviews: ', end='')
	reviews_list = ParseReviews("http://www.amazon.com" + all_reviews[0])
	print('')

	data = {
		'ratings':ratings_dict,
		'reviews':reviews_list,
		'url':amazon_url,
		'price':product_price,
		'name':product_name
	}
	return(data)

counter = 1
def ParseReviews(review_url, stop_at_iter = None):
	global counter
	# Added Retrying 
	print('.', end='')
	for i in range(5):
		try:
			parser = GetParser(review_url)

			XPATH_REVIEW_SECTION_1 = '//div[@data-hook="review"]'
			reviews = parser.xpath(XPATH_REVIEW_SECTION_1)
			reviews_list = []
			
			if not reviews:
				raise ValueError('unable to find reviews in page')

			#Parsing individual reviews
			for review in reviews:
				XPATH_AUTHOR = './/a[@data-hook="review-author"]//text()'
				raw_review_author = review.xpath(XPATH_AUTHOR)
				author = ' '.join(' '.join(raw_review_author).split())

				XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
				raw_review_rating = review.xpath(XPATH_RATING)
				review_rating = ''.join(raw_review_rating).replace(' out of 5 stars','')

				XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
				raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
				review_header = ' '.join(' '.join(raw_review_header).split())

				XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
				raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
				review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')

				XPATH_REVIEW_TEXT_1 = './/span[@data-hook="review-body"]//text()'
				XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
				XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'			
				raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
				raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
				raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)
				review_text = ' '.join(' '.join(raw_review_text1).split())

				#grabbing hidden comments if present
				if raw_review_text2:
					json_loaded_review_data = json.loads(raw_review_text2[0])
					json_loaded_review_data_text = json_loaded_review_data['rest']
					cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
					full_review_text = review_text+cleaned_json_loaded_review_data_text
				else:
					full_review_text = review_text
				if not raw_review_text1:
					full_review_text = ' '.join(' '.join(raw_review_text3).split())

				XPATH_REVIEW_COMMENTS = './/span[@class="review-comment-total aok-hidden"]//text()'
				raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
				review_comments = ''.join(raw_review_comments)
				review_comments = re.sub('[A-Za-z]','',review_comments).strip()

				XPATH_REVIEW_HELPFUL = './/span[@data-hook="helpful-vote-statement"]//text()'
				raw_review_helpful = review.xpath(XPATH_REVIEW_HELPFUL)
				if len(raw_review_helpful) > 0:
					review_helpful = ''.join(raw_review_helpful[0])
					review_helpful = re.sub('[^0-9]','',review_helpful).strip()				
				else:
					review_helpful = '0'
				if review_helpful == "":
					review_helpful = '0'

				XPATH_REVIEW_VERIFIED = './/span[@data-hook="avp-badge"]//text()'
				raw_review_verified = review.xpath(XPATH_REVIEW_VERIFIED)
				if len(raw_review_verified) > 0:
					review_verified = True
				else:
					review_verified = False

				review_dict = {	
					'review_text':full_review_text,
					'review_posted_date':review_posted_date,
					'review_header':review_header,
					'review_rating':review_rating,
					'review_author':author,
					'review_verified_purchaser':review_verified,
					'review_comment_count':review_comments,
					'review_helpful_count':review_helpful
				}
				reviews_list.append(review_dict)

			#stop early if testing
			if stop_at_iter and counter == stop_at_iter:
				return reviews_list
			else:
				counter += 1

			XPATH_NEXT_REVIEWS = '//li[@class="a-last"]//a/@href'
			all_reviews = parser.xpath(XPATH_NEXT_REVIEWS)	
			if all_reviews:
				new_data = ParseReviews("http://www.amazon.com" + all_reviews[0], stop_at_iter)
				if (new_data != None):
					reviews_list += new_data
				return reviews_list
			else:
				return None
		except ValueError:
			print("Retrying to get the correct response")
	
	return None
			
def ReadAsin(asin, json_filename):
	#Add your own ASINs here 
	AsinList = [asin]
	extracted_data = []
	for asin in AsinList:
		print("Downloading and processing page for asin: " + asin)
		extracted_data.append(FindAllReviews(asin))
		if len(AsinList) > 1:
			sleep(5)
	f=open(json_filename,'w')
	json.dump(extracted_data,f,indent=4)

def ReadReviews(filename):
	# read the json data
	json_data=open("data.json").read()
	return(json.loads(json_data))

def CleanReviews(reviews, write_cleaned_data):
	# sort reviews by author
	sorted_list = sorted(reviews, key=lambda k: k['review_author'])

	# remove reviews that are too similar
	similar_removed = []
	for i in range(len(sorted_list)):
		if i != 0:
			shared_items = set(sorted_list[i].items()) & set(sorted_list[i-1].items())
			if len(shared_items) < 4:
				similar_removed.append(sorted_list[i-1])
	similar_removed.append(sorted_list[-1])

	if write_cleaned_data == True:
		# write the sorted/cleaned json
		f=open('data_sorted.json','w')
		json.dump(similar_removed,f,indent=4)

	return(similar_removed)

def GetReviewFields(clean_data):
	#pull out the review text and the titles for good and bad
	text = ""
	titles_good = ""
	titles_bad = ""
	for review in clean_data:
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
	output_text = ""
	trigram_measures = nltk.collocations.TrigramAssocMeasures()
	for ngram, pmi in finder.score_ngrams(trigram_measures.pmi)[:20]:
		content = ' '.join(ngram)
		output_text = output_text + '|' + '|'.join([content[:]]*int(pmi))

	review_fields = {
		"review_text": output_text,
		"review_titles_good": titles_good,
		"review_titles_bad": titles_bad
	}
	return(review_fields)

def ShowWordcloud(image):
	plt.figure()
	plt.imshow(image, interpolation="bilinear")
	plt.axis("off")
	plt.show()

def GenerateWordclouds(review_fields):
	# Create Word Cloud for review text
	wordcloud = WordCloud(max_font_size=40, regexp="[\w\s]+", collocations=False).generate(review_fields["review_text"])
	ShowWordcloud(wordcloud)

	# Create word cloud for title text (good)
	wordcloud = WordCloud(scale=.5, max_font_size=40, max_words=20, colormap="YlGn")
	wc_output = wordcloud.generate(review_fields["review_titles_good"])
	ShowWordcloud(wc_output)

	# Create word cloud for title text (bad)
	wordcloud = WordCloud(width=200, height=100, max_font_size=40, max_words=20, colormap="OrRd").generate(review_fields["review_titles_bad"])
	ShowWordcloud(wordcloud)

def ProcessArgs(argv):
	try:
		opts, args = getopt.getopt(argv,"hcwga:",["help", "cache", "write", "generate", "asin="])
	except getopt.GetoptError:
		print('ARTC.py [-h|--help] [-c|--cache] [-w|--write] [-g|--generate] -a|--asin="Amazon ASIN #"')
		sys.exit(2)
	args_dict = {
		"write":False,
		"generate":False,
		"cache":False,
		"asin":""
	}
	for opt, arg in opts:
		if opt in ('-h', "--help"):
			print('ARTC.py [-h|--help] [-c|--cache] [-w|--write] [-g|--generate] -a|--asin="Amazon ASIN #"')
			sys.exit()
		elif opt in ("-c", "--cache"):
			args_dict["cache"] = True
		elif opt in ("-w", "--write"):
			args_dict["write"] = True
		elif opt in ("-g", "--generate"):
			args_dict["generate"] = True
		elif opt in ("-a", "--asin"):
			args_dict["asin"] = arg
	if args_dict["asin"] == "":
		print("ASIN is required")
		sys.exit()
	return(args_dict)

if __name__ == '__main__':
	json_filename = "data.json"
	args_dict = ProcessArgs(sys.argv[1:])
	if args_dict['cache'] == False:
		ReadAsin(args_dict['asin'], json_filename)
	data = ReadReviews(json_filename)
	clean_data = CleanReviews(data[0]["reviews"], args_dict["write"])
	if args_dict["generate"] == True:
		review_fields = GetReviewFields(clean_data)
		GenerateWordclouds(review_fields)
