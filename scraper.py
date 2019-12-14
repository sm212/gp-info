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
	doctor_info = parse_doctor_info(soup)

	overview_info = {**key_info, **doctor_info}

	return(overview_info)


def get_reviews(practice_id, include_response = True):
	"Get all reviews for practice ID"
	pass