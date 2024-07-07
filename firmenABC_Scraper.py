from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import unquote

options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument('--headless')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Replace with search term of choice
search_term = 'blume'
# Filename of txt file which holds email and company name
filename = 'FirmenABC_EmailsAndCompanyNames.txt'

try:
    driver.get(f'https://www.firmenabc.at/result.aspx?what={search_term}&where=&exact=false&inTitleOnly=false&l=&si=0&iid=&sid=&did=&cc=')
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')))
except TimeoutException:
    print("ERROR: Search failed.")

# Get last page number
main_col = driver.find_element(By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')
nav_pagination = main_col.find_element(By.TAG_NAME, 'nav')
pagination = nav_pagination.find_element(By.TAG_NAME, 'ol')
page_links = pagination.find_elements(By.TAG_NAME, 'li')
last_page = page_links[-1].find_element(By.TAG_NAME, 'a').get_attribute('href')
get_number = last_page.split('&si=')[1].split('&iid=')[0]

for i in range(0, int(get_number) + 1, 50):
    print('#' * 20, 'URLs from ', i, ' --- ', i + 50, '#' * 20)
    try:
        driver.get(f'https://www.firmenabc.at/result.aspx?what={search_term}&where=&exact=false&inTitleOnly=false&l=&si={i}&iid=&sid=&did=&cc=')
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')))
    except TimeoutException:
        print("ERROR: Search failed.")

    # Get links main col div
    main_col = driver.find_element(By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')
    link_list = main_col.find_elements(By.CLASS_NAME, 'bottom-links-item')

    url_lst = []
    for e in link_list:
        if e.find_element(By.TAG_NAME, 'a').get_attribute('href') not in url_lst:
            url_lst.append(e.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    for url in url_lst:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')))
            # Get email
            main_col = driver.find_element(By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')
            mailto_link = main_col.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]').get_attribute('href')
            email = mailto_link.split('mailto:')[1].split('?')[0]
            decoded_email = unquote(email)
            # Get company name and city
            company_name = main_col.find_element(By.CLASS_NAME, 'info')
            # Final string
            final_str = decoded_email + ", " + company_name.text

            print(final_str)

            # Write data directly to file
            try:
                with open(filename, 'r') as file:
                    existing_content = file.read()
            except FileNotFoundError:
                existing_content = ""

            if final_str not in existing_content:
                with open(filename, 'a') as file:
                    file.write(final_str + "\n")
                print(f"Write {final_str} to {filename}.")
            else:
                print(f"ALREADY EXISTS: {final_str} already exits in {filename}.")

        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")
            continue

driver.quit()
