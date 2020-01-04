from bs4 import BeautifulSoup
import requests as r
import pandas as pd

def get_practice_ids():
    "Returns a list of GP practice IDs from the NHS site"

    page = r.get('https://www.nhs.uk/Services/Pages/HospitalList.aspx?chorg=GpBranch')
    soup = BeautifulSoup(page.content, 'lxml')
    
    links = [link.get('href') for link in soup.find_all('a')]
    ids = [link.split('=')[1] for link in links if '=' in link]
    
    return(ids)

def make_soup(url):
	"Checks if the practice profile is not hidden"
	
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
		print('Practice {} is hidden'.format(practice_id))
		return(None)

	key_info = parse_key_info(soup)

	return(key_info)

def get_reviews(practice_id):
	"Get all reviews for practice ID"
	
	base_url = 'https://www.nhs.uk/Review/List/P{}?currentpage={}'
	url = base_url.format(practice_id, 1)

	soup = make_soup(url)

	if soup is None:
		print('Practice {} is hidden'.format(practice_id))
		return(None)
	elif soup.find(class_ = 'nhsuk-u-margin-bottom-0') is None:
		print('Practice {} has no reviews'.format(practice_id))
		return(None)

	n_reviews = int(soup.find(class_ = 'nhsuk-u-margin-bottom-0').text.split()[-1])
	n_pages = n_reviews / 10 + (n_reviews % 10 > 0) # 10 reviews per page, need to round up
	n_pages = int(n_pages)

	for i in range(1, n_pages + 1):
		url = base_url.format(practice_id, i)
		page = r.get(url)
		soup = BeautifulSoup(page.content, 'lxml')

		review_boxes = soup.find_all(attrs = {'role' : 'listitem'})
		for box in review_boxes:
			review_soup = box.find(attrs = {'aria-label' : 'Organisation review'}) 
			reply_soup = box.find(attrs = {'aria-label' : 'Organisation review response'})
			
			review = parse_text(review_soup)
			review_date = parse_date(review_soup)
			rating = parse_rating(review_soup)
			reply = parse_text(reply_soup)
			reply_date = parse_date(reply_soup)

	review_dict = {'id' : i ,'review' : review, 'review_date' : review_date,
				   'rating' : rating, 'reply' : reply, 'reply_date' : reply_date}

	return(review_dict)

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
		
		return(p_tags[review_index].text)

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

	key_info_data = [tag.text for tag in soup.find_all(class_ = 'indicator-value')]
	key_info_keys = ['patients', 'evening_weekend', 'would_rec']

	if len(key_info_data) == 3:
		key_info = {key: data for key, data in zip(key_info_keys, key_info_data)}
		# Fix datatypes & add in survey response numbers
		key_info['patients'] = int(key_info['patients'])
		key_info['would_rec'] = int(key_info['would_rec'][:-1]) / 100
		key_info['n_asked_rec'] = int(soup.find_all(class_ = 'indicator-text')[-1].text.split()[-2])
	else:
		key_info = {'patients' : 'NA', 'would_rec' : 'NA', 'n_asked_rec' : 'NA'}
	return(key_info)