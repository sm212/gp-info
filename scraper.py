from bs4 import BeautifulSoup
import requests as r

def get_practice_ids():
    "Returns a list of GP practice IDs from the NHS site"

    page = r.get('https://www.nhs.uk/Services/Pages/HospitalList.aspx?chorg=GpBranch')
    soup = BeautifulSoup(page.content)
    
    links = [link.get('href') for link in soup.find_all('a')]
    ids = [link.split('=')[1] for link in links if '=' in link]
    
    return(ids)

def get_overview(practice_id):
	"Get overview information for practice ID"

	base_url = 'https://www.nhs.uk/Services/GP/Overview/DefaultView.aspx?id={}'
	url = base_url.format(practice_id)

	page = r.get(url)
	soup = BeautifulSoup(page.content)

	key_info = parse_key_info(soup)

	return(key_info)

def parse_key_info(soup):
    "Parse data from the 'Key Information' box of an overview page"

    key_info_data = [tag.contents[0] for tag in soup.find_all(class_ = 'indicator-value')]
    key_info_keys = ['patients', 'evening_weekend', 'would_rec']
    key_info = {key: data for key, data in zip(key_info_keys, key_info_data)}

    # Fix datatypes & add in survey response numbers
    key_info['patients'] = int(key_info['patients'])
    key_info['would_rec'] = int(key_info['would_rec']) / 100
    key_info['n_asked_rec'] = int(soup.find_all(class_ = 'indicator-text')[-1].contents[0].split()[-2])
    
    return(key_info)

def get_reviews(practice_id):
	"Get all reviews for practice ID"
	
	base_url = 'https://www.nhs.uk/Review/List/P{}?currentpage={}'
	url = base_url.format(practice_id, 1)

	page = r.get(url)
	soup = BeautifulSoup(page.content)

	n_reviews = int(soup.find(class_ = 'nhsuk-u-margin-bottom-0').text.split()[-1])
	n_pages = n_reviews / 10 + (n_reviews % 10 > 0) # 10 reviews per page, need to round up

	reviews = []
	review_dates = []
	ratings = []
	replies = []
	reply_dates = []

	for i in range(1, n_pages + 1):
		url = base_url.format(practice_id, i)
		page = r.get(url)
		soup = BeautifulSoup(page.content)

		review_boxes = soup.find_all(attrs = {'role' : 'listitem'})
		for box in review_boxes:
			review_soup = box.find(attrs = {'aria-label' : 'Organisation review'}) 
			reply_soup = box.find(attrs = {'aria-label' : 'Organisation review response'})
			
			reviews.append(parse_text(review_soup))
			review_dates.append(parse_date(review_soup))
			ratings.append(parse_rating(review_soup))
			replies.append(parse_text(reply_soup))
			reply_dates.append(parse_date(reply_soup))

	review_dict = {'reviews' : reviews, 'review_dates' : review_dates,
				   'ratings' : ratings, 'replies' : replies, 'reply_dates' : reply_dates}

	return(review_dict)