
# Scrape indeed.com for Jobs data
# get: company name, company location, job title, salary and total jobs.

# import module
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re


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
        sal = job.find(class_="salary-snippet")
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
    # NOTE getting 'new' at front of strings
    result.pop()
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
    total_jobs = re.sub(r'Page\s\d\d?\d?\sof\s', '', total_jobs)
    return total_jobs


# driver nodes/main function
if __name__ == "__main__":
    # Data for URL
    job = "data+science+analyst"  # "private+chauffeur"
    Location = "London"
    last_x_days = "7"
    base_url = "https://uk.indeed.com/jobs?q="+job+"&l="+Location+"&fromage="+last_x_days

    total_jobs = get_total_jobs(base_url)
    print(f'{total_jobs} for {job}')

    # lists
    job_res = []
    com_res = []
    sal = []
    com_loc = []

    num = 0
    while num < 1000:
        page = int(0)
        url = base_url
        try:
            page = str(page + num)
            print(f'Number of jobs processed is: {page}')
            url = url+"&start="+page

            # Captcha - get around bot stopper with radom number sleep
            rand_num = random.uniform(1, 2)
            print(rand_num)
            time.sleep(rand_num)

            # Get soup
            soup = html_code(url)

            # call funcs to get data and store in lists
            job_res.extend(job_title(soup))
            com_res.extend(company_name(soup))
            com_loc.extend(company_location(soup))
            sal.extend(salary(soup))

            print(len(job_res))
            print(len(com_res))
            print(len(com_loc))
            print(len(sal))

            num += 15
        except:
            print('Problem')
            break

# make list of list
l = []
l.append(job_res)
l.append(com_res)
l.append(com_loc)
l.append(sal)
# transpose list of lists so it fits into a df
l = list(map(list, zip(*l)))
df = pd.DataFrame(l, columns=['job_title', 'company_name', 'company_location', 'salary'])
print(df.head())
df.to_excel(r'Indeed_job_data\output\indeed_jobs_scan.xlsx')
print('Saved to Excel')


# TODO - Captcha is stopping me - FIXED
# TODO - push data to df - DONE
# TODO - stop blank row getting added to data - DONE
# TODO - final output has some repetition
# TODO - add 'job' as another column
# TODO - push data to DB
# TODO - get common words from the content maybe skills e.g. SQL, Python.
