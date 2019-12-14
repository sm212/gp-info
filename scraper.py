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
	pass

def get_reviews(practice_id, include_response = True):
	"Get all reviews for practice ID"
	pass