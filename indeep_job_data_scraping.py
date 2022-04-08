
# Scrape indeed.com for Jobs data
# get: company name, company location, job title, salary and total jobs.

# import module
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
import os
from datetime import date, datetime, timedelta
import sqlite3

print(os.getcwd())


def getdata(url):
    # Make request and grab data
    r = requests.get(url)
    return r.text


def html_code(url):
    # pass the data with BS4 and return soup
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')
    return soup


def salary(soup):
    # find the Html tag with find() and convert into string
    data_str = ""
    result = ""
    job_card = soup.find_all(class_="jobCard_mainContent")
    for job in job_card:
        # sal = job.find(class_="salary-snippet")   # not catching all sals
        sal = job.find(class_="salary-snippet-container")
        if sal is None:
            data_str = data_str + "No Salary provided" + "\n"
        else:
            data_str = data_str + sal.get_text() + "\n"
    result = data_str.split("\n")
    result.pop()  # remove unwanted last blank element from list
    return result


def job_title(soup):
    # find the Html tag with find() and convert into string
    data_str = ""
    result = ""
    for item in soup.find_all(class_="jobTitle"):  # jobtitle turnstileLink   # "a",
        data_str = data_str + item.get_text() + "\n"
    data_str = re.sub(r'new', '', data_str)  # remove unwanted 'new'
    result = data_str.split("\n")
    result.pop()
    # print(len(result))
    return result


def company_name(soup):
    # find the Html tag with find() and convert into string
    data_str = ""
    result = ""
    for item in soup.find_all(class_="companyName"):
        data_str = data_str + item.get_text() + "\n"
    result = data_str.split("\n")
    result.pop()
    return result


def company_location(soup):
    # find the Html tag with find() and convert into string
    data_str = ""
    result = ""
    for item in soup.find_all(class_="companyLocation"):
        data_str = data_str + item.get_text() + "\n"
    result = data_str.split("\n")
    result.pop()
    return result


def get_total_jobs(url):
    soup = html_code(url)
    total_jobs = soup.find("div", {"id": "searchCountPages"})
    total_jobs = total_jobs.string.strip()
    # total_jobs = re.sub(r'Page\s\d\d?\d?\sof\s', '', total_jobs)
    total_jobs = re.search(r'(\d\d?\d?)\sjobs', total_jobs)[1]
    return total_jobs


def get_page_num(soup):
    """Func to get the page number"""
    page_num = soup.find("div", {"id": "searchCountPages"})
    page_num = page_num.string.strip()
    page_num = re.sub(r'\sof\s\d\d?\d?\sjobs', '', page_num)
    return page_num


def get_job_id(soup):
    """Func to extract the unquie job id
    PROBLEM ID is not consistent!!!
    """
    data_str = ""
    result = ""
    for item in soup.find_all("a", {'class': ["cardOutline", "tapItem", 'fs-unmask']}):  # True,
        print(item['data-jk'])
        # NOTE this is not working consistently.
        data_str = data_str + item['data-jk'] + "\n"
    result = data_str.split("\n")
    result.pop()
    return result


def get_date_added(soup):
    # data_str = ""
    # date_added = ""
    date_added_list = []
    for item in soup.find_all(class_="date"):
        try:
            item = re.search(r'\d\d?\d?', item.get_text())[0]
            item = date.today() - timedelta(days=int(item))
        except:
            item = date.today()
        date_added_list.append(item)
        # data_str = data_str + item + "\n"
    # date_added = data_str.split("\n")
    return date_added_list


# driver nodes/main function
if __name__ == "__main__":
    # Data for URL
    job = "data+science+analyst"  # "private+chauffeur"
    Location = "London"
    last_x_days = "7"
    base_url = "https://uk.indeed.com/jobs?q="+job+"&l="+Location+"&fromage="+last_x_days
    print(base_url)

    total_jobs = get_total_jobs(base_url)
    print(f'There are {total_jobs} add in the last {last_x_days} for {job}')

    # lists
    # job_id = []
    job_res = []
    com_res = []
    sal = []
    com_loc = []
    date_added = []

    num = 0
    # check number of jobs for search and use that number
    # but restrict max 300 jobs download.
    if int(total_jobs) > 200:
        restrictor = 200
    else:
        restrictor = total_jobs

    page = int(0)
    while num < int(restrictor):
        url = base_url
        # try:
        page = str(num)
        # print(f'Number of jobs processed is: {page}')
        url = url + "&start=" + page

        # Captcha - get around bot stopper with radom number sleep
        rand_num = random.uniform(1, 2)
        print(rand_num)
        time.sleep(rand_num)

        # Get soup
        soup = html_code(url)

        # call funcs to get data and store in lists
        # job_id.extend(get_job_id(soup))
        job_res.extend(job_title(soup))
        com_res.extend(company_name(soup))
        com_loc.extend(company_location(soup))
        sal.extend(salary(soup))
        date_added.extend(get_date_added(soup))

        # page_num.extend((get_page_num(soup)))

        print(len(job_res))
        print(len(com_res))
        print(len(com_loc))
        print(len(sal))
        # print(len(job_id))
        print(f'Page number is: {get_page_num(soup)}')

        num += 10

# make list of list
l = []
l.append(job_res)
l.append(com_res)
l.append(com_loc)
l.append(sal)
l.append(date_added)
# l.append(job_id)
# transpose list of lists so it fits into a df
l = list(map(list, zip(*l)))
df = pd.DataFrame(l, columns=['job_title', 'company_name', 'company_location', 'salary', 'date_added'])
# remove duplicate values
print(df.shape)
df = df.drop_duplicates()
print(df.shape)


def map_to_job_category(x):
    """Func to map job Category if job title contains string"""
    cat_map = {'Analyst': 'Data Analyst',
               'Scientist': 'Data Scientist',
               'Data Science': 'Data Scientist',
               'Engineer': 'Data Engineer'}

    group = "unknown"
    for key in cat_map:
        if key in x:
            group = cat_map[key]
            break
    return group


# add new column with category
df['job_category'] = df['job_title'].apply(map_to_job_category)

# add column with todays date
df['date_scrapped'] = pd.Timestamp.today()
print(df.head())
# df.to_excel(r'..\Indeed_job_data\output\indeed_jobs_scan.xlsx')
# path = r'C:\Users\goldsby_c\OneDrive - Pearson PLC\Add-hoc analysis projects\Indeed_job_data\output\indeed_jobs_scan.xlsx'
# df.to_excel(path)
# print('Saved to Excel')

print('------------ save to DB ---------------')
# conn = sqlite3.connect(r'.\Indeed_job_data\indeed_jobs_db.db') # started to get error with this so using full path

conn = sqlite3.connect(
    r'C:\Users\goldsby_c\OneDrive - Pearson PLC\Add-hoc analysis projects\Indeed_job_data\indeed_jobs_db.db')


conn.execute('''CREATE TABLE IF NOT EXISTS JOBS
                (job_title TEXT,
                company_name TEXT,
                company_location TEXT,
                salary TEXT,
                date_added DATE,
                date_scrapped DATETIME,
                job_category TEXT
                )''')

df.to_sql('JOBS',  con=conn, if_exists='append', index=False)
print(pd.read_sql_query("SELECT * FROM JOBS LIMIT 10", conn))
# conn.execute("SELECT * FROM JOBS LIMIT 10").fetchall()

# TODO - Captcha is stopping me - FIXED
# TODO - push data to df - DONE
# TODO - stop blank row getting added to data - DONE
# TODO - final output has some repetition
# TODO - add date data scrapped - DONE
# TODO - add 'job' as another column - DONE
# TODO - push data to DB - DONE
# TODO - add extra fields?
# TODO - get common words from the content maybe skills e.g. SQL, Python.
