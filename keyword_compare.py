import requests
from webscraper import pagination, extract_job_postings

keywords = ['developpeur', 'informatique', 'data scientist', 'data analyst', 'data engineer', 'machine learning', 'deep learning', 'intelligence artificielle' 'python', 'R', 'scala', 'tensorflow', 'keras', 'pytorch' 'numpy', 'pandas', 'hadoop', 'spark']

url = 'https://www.indeed.fr/emplois'

keyword = keywords[0]

params = {
'q': keyword,
'l': "france",
'radius': 0,
'sort': 'date',
'fromage': 7,
'limit': 50,
'start': 0
}


start_page = requests.get(url, params=params)
start_values = pagination(start_page)

jobs = extract_job_postings(start_page, start_values)

def extract_job_info(job):

    id = job.attrs['id']
    title = job.find("a")["title"]

    job_info_dict = {
    "job_id": id,
    "job_title": title,
    }

    return job_info_dict
