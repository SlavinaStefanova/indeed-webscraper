import requests
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
import datetime as dt
import maya

url = 'https://www.indeed.fr/emplois'
params = {
'q': "tensorflow",
'l': "france",
'radius': 0,
'sort': 'date',
'fromage': 7,
'limit': 50,
'start': 0
}

start_page = requests.get(url, params=params)
timestamp = start_page.headers['date']
timestamp_dt = maya.parse(timestamp).datetime(to_timezone='Europe/Paris', naive=True)

def pagination(start_page):

    try:
        pagination = SoupStrainer('div', class_='pagination')
        pag_soup = BeautifulSoup(start_page.text, 'html.parser', parse_only=pagination)
        last_page = pag_soup.select(".pn")[-2].text
        last_page = int(last_page)
        start_values = [str(i * 50) for i in range(1, last_page)]
        return start_values
    except:
        return []

start_values = pagination(start_page)

def extract_job_postings(start_page, start_values, job_list=[]):

    soup = BeautifulSoup(start_page.text, 'html.parser')
    for job in soup.select(".jobsearch-SerpJobCard"):
        job_list.append(job)

    try:
        next_start_value = start_values.pop(0)
        params['start'] = next_start_value
        next_page = requests.get(next_url, params=params)
        return extract_job_postings(next_page, start_values, job_list)
    except IndexError:
        return job_list

jobs = extract_job_postings(start_page, start_values)
print(len(jobs))


def format_post_date(date_string):

    '''Takes a string of the type "Publiée il y a 2 jours" and returns a formatted date string such as "03-05-2018"'''

    date = date_string.split(' ')

    if "l'instant" in date or "Aujourd'hui" in date:
        days_ago = 0
    elif "jour" in date:
        days_ago = 1
    elif "jours" in date and "30+" not in date:
        days_ago = int(date[-2])
    else:
        return "This post is too old"

    delta = dt.timedelta(days=days_ago)

    format = "%d-%m-%Y"
    date_scraped = timestamp_dt.date()
    date_posted = (date_scraped - delta).strftime(format)
    return date_posted

def extract_job_info(job):

    date_format = "%d-%m-%Y"
    date_scraped = timestamp_dt.date().strftime(date_format)
    date_posted_raw = job.find('span', class_='date').get_text()

    job_dict = {
    "job_id": job.attrs['id'],
    "job_title": job.find('a', attrs={'data-tn-element':"jobTitle"}).text.strip(),
    # "company": job.find('span', class_='company').text.strip(),
    "location": job.find('span', class_='location').get_text(),
    # "job_summary": job.find('span', class_='summary').text.strip(),
    # "job_link": "https://www.indeed.fr" + job.find('h2', attrs={"class": "jobtitle"}).find('a')['href'],
    "date_posted": format_post_date(date_posted_raw),
    "date_scraped": date_scraped
    }

    return job_dict

# job_info = extract_job_info(jobs[0])
# print(job_info)
