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

email_lst = []

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

    # TODO: Get also Company Name and Name of Company Owner
    url_lst = []
    for e in link_list:
        if e.find_element(By.TAG_NAME, 'a').get_attribute('href') not in url_lst:
            url_lst.append(e.find_element(By.TAG_NAME, 'a').get_attribute('href'))

    for url in url_lst:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')))

            main_col = driver.find_element(By.CSS_SELECTOR, '#main-container > div > div.col-sm-8.main-col')
            mailto_link = main_col.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]').get_attribute('href')
            email = mailto_link.split('mailto:')[1].split('?')[0]
            decoded_email = unquote(email)
            email_lst.append(decoded_email)
            print(decoded_email)
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")
            continue

print(email_lst)
driver.quit()
