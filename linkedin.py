from selenium import webdriver
import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
from babel import Locale
def get_currency_code(symbol):
    locale = Locale('en')
    currency_data = locale.currency_symbols
    currency_code = next((code for code, sym in currency_data.items() if sym == symbol), None)
    return currency_code

def convert_to_dollars(salary_str):
    # Extract the currency and amount from the salary string
    pattern = r'([^\d]+)([\d,]+)'
    matches = re.findall(pattern, salary_str)

    # Extract the symbol and numeric values from the matches
    symbol, numeric = matches[0]

    # Remove any commas from the numeric values
    numeric = numeric.replace(',', '')
    symbol = symbol.strip()

    # Get the currency code based on the symbol
    currency_code = get_currency_code(symbol)

    # Fetch the exchange rate data from the API
    base_currency = currency_code
    target_currency = 'USD'
    endpoint = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
    response = requests.get(endpoint)
    exchange_rates = response.json()['rates']

    # Convert currency to USD
    converted_amount = float(numeric) * exchange_rates[target_currency]

    return converted_amount

keyword = 'Lead Software Engineer'
location = 'worldwide'
url1 = f'https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'

driver_path = r'chromedriver.exe'
service = Service(driver_path)

driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
driver.implicitly_wait(10)
driver.get(url1)
print(driver.current_url)
if 'authwall' in driver.current_url or 'signin' in driver.current_url:
    driver.get(url1)
    print(url1)
    print("run")
    driver.implicitly_wait(10)
y = driver.find_elements(By.CLASS_NAME, 'results-context-header__job-count')[0].text
print("y" + y)
n = int(''.join(filter(str.isdigit, y)))
print("n" + str((n + 200) / 25))
i = 2
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# i <= int((n + 200) / 25) + 1:
while i <= 1:
    print("i" + str(i))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i = i + 1

    try:
        send = driver.find_element(By.XPATH, "//button[@aria-label='See more jobs']")
        driver.execute_script("arguments[0].click();", send)
        time.sleep(1)

    except:
        pass
        time.sleep(0.1)

jobs = []
j=1
try:
    job_elements2 = driver.find_elements(By.CSS_SELECTOR, '[data-tracking-control-name="public_jobs_jserp-result_search-card"]')
    job_elements = driver.find_elements(By.CLASS_NAME, 'base-search-card__info')
    # print(len(job_elements)) 
    # metadata_elements = driver.find_elements(By.CLASS_NAME, 'base-search-card__metadata')
    for job_element in job_elements2:
        job = {
            'title': '',
            'company': '',
            'location': '',
            'site': '',
            'salary': '',
            'salary_min_usd': '',
            'salary_max_usd': '',
            'listing_date': '',
            'link': '',
            'job_description': '',
            'email_ids': '',
            'number_of_applicants': '',
            'seniority_level': '',
            'Employment type': '',
            'posted-time': ''
        }
        print(len(job_elements2))
        job['title'] = driver.find_elements(By.CLASS_NAME, 'base-search-card__title')[j-1].text
        job['company'] = driver.find_elements(By.CLASS_NAME, 'base-search-card__subtitle')[j-1].text
        job['location'] = job_listing_date_element = driver.find_elements(By.CLASS_NAME, 'job-search-card__location')[j-1].text
        job['site'] = "LinkedIn"
        try:
                flag=0
               

                # job['salary'] = driver.find_elements(By.CLASS_NAME, 'base-search-card__metadata')[j-1].find_element(By.CSS_SELECTOR, 'span.job-search-card__salary-info').text
                job['salary'] =  driver.execute_script(
                    "return arguments[0].querySelector('.base-search-card__metadata span.job-search-card__salary-info').textContent;", 
                    job_elements[j-1]
                )
                salary_values = re.findall(r'[\d,]+', job['salary'])

                if len(salary_values) >= 2:
                    salary_min, salary_max = job['salary'].split('-')
                    job['salary_min_usd'] = convert_to_dollars(salary_min.strip())
                    job['salary_max_usd'] = convert_to_dollars(salary_max.strip())
                else:
                    # Set default values if only one salary value is present
                    job['salary_min_usd'] = convert_to_dollars(job['salary'])
                    job['salary_max_usd'] = job['salary_min_usd']
                #job['salary'] = convert_to_dollars(salary_min)
                #print(job['salary'])
        except:
                job['salary'] = None
                job['salary_min_usd'] = None
                job['salary_max_usd']= None
                # time.sleep(2)
                # job['salary']='INR102-INR200'
                # salary_min, salary_max = job['salary'].split('-')
                # job['salary'] = convert_to_dollars(salary_min)
               

        try:
            # job_listing_date_element = driver.find_elements(By.CLASS_NAME, 'job-search-card__listdate')[j-1]
            job['listing_date'] = driver.find_elements(By.CLASS_NAME, 'job-search-card__listdate')[j-1].get_attribute('datetime')
        except:
            current_date = datetime.now().date()
            # formatted_date = current_date.strftime('%m/%d/%Y')
            job['listing_date'] = current_date.strftime('%m/%d/%Y')        #   
        max_retries=3
        retry_delay = 2
        # job_link_element = job_element
        for retry in range(max_retries):
            try:
                job_link_element = job_element
                
                job_link_element.click()
                time.sleep(1)
                if j%5==0:    
                    time.sleep(5)
                # time.sleep(10)
                # if not (driver.find_element(By.CLASS_NAME, 'description__job-criteria-text').text):
                #     job_elements2[j].click()    
                #     time.sleep(1)
                #     job_link_element.click()
                #     time.sleep(1)
                break  # Break the retry loop if the job click is successful
                
            except:
                print(f"Job click failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        else:
            print(f"Job click failed after {max_retries} retries. Moving on to the next job.")
            continue 
        job['link'] = job_element.get_attribute('href') if job_link_element else None

        # print(job_element.get_attribute('href'))
        if job['link']:
            try:
                button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Show more, visually expands previously read content above']"))
                )
                driver.execute_script("arguments[0].click();", button)
                # time.sleep(2)
            except Exception as e:
                print("Failed to click the 'Show more' button:", str(e))
                flag=1

        
            try:
                job['job_description'] = driver.find_element(By.CLASS_NAME, 'show-more-less-html__markup').text

            except:
                job['job_description'] = None

            try:
                # Use regular expression to find email IDs
                
                email_matches = re.finditer(email_pattern, job['job_description'])
                job['email_ids'] = ', '.join(match.group() for match in email_matches)
                if not job['email_ids']:
                    job['email_ids'] = 'NA'
            except:
                job['email_ids'] = None    
                
            try:
                job['number_of_applicants'] = driver.find_element(By.CLASS_NAME, 'num-applicants__caption').text
            except:
                job['number_of_applicants'] = None
            
            try:
                job['seniority_level'] = driver.find_element(By.CLASS_NAME, 'description__job-criteria-text').text
            except:
                job['seniority_level'] = None
   

            try:
                # li_element = driver.find_elements(By.CSS_SELECTOR, 'li.description__job-criteria-item')[1]
                span_element = driver.find_elements(By.CSS_SELECTOR, 'li.description__job-criteria-item')[1].find_element(By.CSS_SELECTOR, 'span.description__job-criteria-text--criteria').text
                job['Employment type'] =span_element

            except:
                job['Employment type'] = None  
            try:

                job['posted-time'] = driver.find_element(By.CSS_SELECTOR, 'span.posted-time-ago__text').text
            except:
                job['posted-time'] = None  
                
            if flag==1:
                job['job_description'] = 'NA'
                job['email_ids'] = 'NA'
                job['number_of_applicants'] = 'NA'
                job['seniority_level'] = 'NA'
                job['Employment type'] = 'NA'
                job['posted-time'] = 'NA'     
            jobs.append(job)
            j=j+1
            print(j-1)
            print("values",job['posted-time'])
        
             

except IndexError:
    print("no")


companyfinal = pd.DataFrame(jobs)
companyfinal.fillna('NA', inplace=True)
companyfinal.to_csv('linkedin.csv', index=False)
