import requests
from bs4 import BeautifulSoup, SoupStrainer
import datetime as dt
import maya
import pprint
import unidecode

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


def format_post_date(date_string):

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
    date_posted_raw = job.find('span', class_='date').get_text()
    date_posted = format_post_date(date_posted_raw)
    date_scraped = timestamp_dt.date().strftime(date_format)

    id = job.attrs['id']
    title = job.find("a")["title"]

    try:
        company = job.find('span', class_='company').text.strip()
    except:
        company = "N/A"
    try:
        location = job.find('span', class_='location').get_text()
    except:
        location = "N/A"
    try:
        summary = job.find('div', class_='summary').get_text().strip()
    except:
        summary = "N/A"
    try:
        link = "https://www.indeed.fr" + job.find('a').attrs['href']
    except:
        link = "N/A"
    try:
        salary = job.find('span', class_='salary no-wrap').text.strip()
        salary = unidecode.unidecode(salary)
    except:
        salary = 'N/A'

    def get_ad(job):
        ad_page = requests.get(link)
        ad = BeautifulSoup(ad_page.text, 'html.parser')
        text = ad.find('div', class_='jobsearch-JobComponent-description').get_text()

        return text

    job_info_dict = {
    "job_id": id,
    "job_title": title,
    "company": company,
    "location": location,
    "salary": salary,
    "summary": summary,
    "link": link,
    "date_posted": format_post_date(date_posted_raw),
    "date_scraped": date_scraped,
    "text": get_ad(job)
    }

    return job_info_dict

# Test code below
if __name__ == '__main__':

    start_page = requests.get(url, params=params)
    timestamp = start_page.headers['date']
    timestamp_dt = maya.parse(timestamp).datetime(to_timezone='Europe/Paris', naive=True)

    start_values = pagination(start_page)

    jobs = extract_job_postings(start_page, start_values)
    print(len(jobs))

    for job in jobs[:3]:
        job_info = extract_job_info(job)
        pprint.pprint(job_info)
        print('\n')
