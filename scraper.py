from bs4 import BeautifulSoup
import requests as r
import pandas as pd
import re

def get_practice_ids():
    "Returns a list of GP practice IDs from the NHS site"

    url = 'https://www.nhs.uk/Services/Pages/HospitalList.aspx?chorg=GpBranch'
    page = r.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    
    links = [link.get('href') for link in soup.find_all('a')]
    ids = [link.split('=')[1] for link in links if '=' in link]
    
    return(ids)

def make_soup(url):
	"Returns BeautifulSoup(url), provided the url is viewable"
	
	page = r.get(url)
	soup = BeautifulSoup(page.content, 'lxml')
	if soup.find(name = 'h1').text != 'Profile Hidden' and \
	   soup.find('h1').text != 'Page not found.':	
		return(soup)
	else:
		return(None)

def get_overview(practice_id):
	"Get overview information for practice ID"

	base_url = 'https://www.nhs.uk/Services/GP/Overview/DefaultView.aspx?id={}'
	url = base_url.format(practice_id)
	soup = make_soup(url)

	if soup is None:
		return(None)

	key_info = parse_key_info(soup)
	address = parse_address(soup)
	key_info['practice_id'] = practice_id
	key_info['address'] = address

	return(key_info)

def get_reviews(practice_id):
	"Get all reviews for practice ID"
	
	base_url = 'https://www.nhs.uk/Review/List/P{}?currentpage={}'
	url = base_url.format(practice_id, 1)

	soup = make_soup(url)

	if soup is None:
		return(None)
	elif soup.find(class_ = 'nhsuk-u-margin-bottom-0') is None:
		return(None)

	n_reviews = soup.find(class_ = 'nhsuk-u-margin-bottom-0').text.split()[-1]
	n_reviews = int(n_reviews)
	n_pages = n_reviews / 10 + (n_reviews % 10 > 0) # 10 reviews per page
	n_pages = int(n_pages)

	review_list = []
	review_id = 0

	for i in range(1, n_pages + 1):
		url = base_url.format(practice_id, i)
		page = r.get(url)
		soup = BeautifulSoup(page.content, 'lxml')

		review_boxes = soup.find_all(attrs = {'role' : 'listitem'})
		for box in review_boxes:
			review_id += 1

			review_soup = box.find(attrs = {'aria-label' : 'Organisation review'}) 
			reply_soup = box.find(attrs = {'aria-label' : 'Organisation review response'})
			
			review = {}
			review['practice_id'] = practice_id
			review['review_id'] = review_id
			review['review'] = parse_text(review_soup)
			review['review_date'] = parse_date(review_soup)
			review['rating'] = parse_rating(review_soup)
			review['reply'] = parse_text(reply_soup)
			review['reply_date'] = parse_date(reply_soup)

			review_list.append(review)

	return(review_list)

def parse_text(soup):
	"Parse text from review and review responses"

	p_tags = soup.find_all(name = 'p')

	if len(p_tags) == 1:
		return('No reply')
	else:
		# Text will be the longest paragraph - all other <p> tags
		# are metadata
		lengths = [len(p.text) for p in p_tags]
		review_index = lengths.index(max(lengths))

		# Remove special characters
		text = p_tags[review_index].text
		text = re.sub(r'[^\w\d\s ,?/!:;_£\-\.]', '', text)
		return(text)

def parse_date(soup):
	"Parse date for a review or review responses"
	
	unparsed_date = soup.find(class_ = 'nhsuk-body-s')
	if unparsed_date is not None:
		date = unparsed_date.text.split()
		year = date[-1]
		month = date[-2]
		day = date[-3]

		month_lookup = {'January' : 1, 'February' : 2, 'March' : 3,
		'April' : 4, 'May' : 5, 'June' : 6, 'July' : 7,
		'August' : 8, 'September' : 9, 'October' : 10,
		'November' : 11, 'December' : 12}

		iso_date = f'{year}-{month_lookup[month]:00}-{day}'
		return(iso_date)
	else:
		# Only way to get here is if there is no date, which can
		# only happen if there's no reply (every review is dated)
		return('No reply')

def parse_rating(soup):
	"Parse rating for a review"
	
	try:
		rating = len(soup.find(class_= 'small-stars').text)
		return(rating)
	except AttributeError:
		return('No rating')

def parse_key_info(soup):
	"Parse data from the 'Key Information' box of an overview page"

	indicator_vals = [t.text for t in soup.find_all(class_ = 'indicator-value')]
	indicator_text = [t.text for t in soup.find_all(class_ = 'indicator-text')]

	key_info = {}

	for i in range(len(indicator_text)):
		val = indicator_vals[i]
		text = indicator_text[i]

		if 'patients' in text:
			key_info['patients'] = val
		elif 'patients' not in key_info.keys():
			key_info['patients'] = 'NA'

		if 'availability' in text:
			key_info['evening_weekend'] = val
		elif 'evening_weekend' not in key_info.keys():
			key_info['evening_weekend'] = 'NA'

		if 'recommend' in text:
			key_info['would_rec'] = val
			key_info['n_asked'] = text.split()[-2]
		elif 'would_rec' not in key_info.keys():
			key_info['would_rec'] = 'NA'
			key_info['n_asked'] = 'NA'

	return(key_info)

def parse_address(soup):
	"Get adress from practise overview"

	address = soup.find(attrs = {'typeof' : 'PostalAddress'}).text.strip()
	return(re.sub(r'\s{2}', '', address))

practice_ids = get_practice_ids()

key_info = []
reviews = []

for i, practice_id in enumerate(practice_ids):

	info = get_overview(practice_id)
	if info is None:
		print('{} / {}  -  Practice ID {} is hidden'.format(i + 1, len(practice_ids), practice_id))
	else:
		key_info.append(info)

	review = get_reviews(practice_id)
	if info is not None and review is None:
		print('{} / {}  -  Practice ID {} has no reviews'.format(i + 1, len(practice_ids), practice_id))
	if review is not None:
		reviews.extend(review)
		print('{} / {}  -  Got data for Practice ID {}'.format(i + 1, len(practice_ids), practice_id))

df_key_info = pd.DataFrame(key_info)
df_reviews = pd.DataFrame(reviews)

df_key_info.to_csv('key_info.csv', index=False)
df_reviews.to_csv('reviews.csv', index=False)