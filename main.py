import json
import os.path
import re
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd


def setup_driver():
    # 使用WebDriverManager来获取Chrome WebDriver
    # chrome_service = Service(ChromeDriverManager().install())
    chrome_options = Options()

    # 创建一个 Chrome WebDriver 实例
    # driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    return driver


def banner_handler(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "banniere-consentement-temoins"))
    )
    # Look for the accept button within the banner
    # Wait for the button to be clickable
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'ct_btn-accepter-tous')))

    # Click the button
    time.sleep(2)
    button.click()


def navigate_old(url):
    driver = setup_driver()
    driver.set_window_size(1280, 800)
    driver.get(url)
    all_data = []

    banner_handler(driver)
    time.sleep(10)
    select_entries_per_page(driver)

    page = 1
    last_page = False
    try:
        while not last_page:
            # Extract data from current page
            print(f'processing the Page {page}...', end='\t')
            page_data = extract_table_data(driver)
            all_data.extend(page_data)
            print(f'Page {page} finished')

            # Try to find and click the "Next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Page suivante']")
                if 'v-btn--disabled' in next_button.get_attribute('class'):
                    print("This is the last page.\nFinished!")
                    break
                next_button.click()
                time.sleep(20)  # Wait for the next page to load
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
            page += 1
    finally:
        # time.sleep(1000)
        driver.quit()

    return all_data


def select_entries_per_page(driver):
    try:
        # find footer
        footer = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "v-data-footer"))
        )
        # Click on the dropdown to open it
        dropdown = footer.find_element(By.CSS_SELECTOR, "div[role='button'][aria-haspopup='listbox']")

        dropdown.click()
        time.sleep(1)

        # Select the option for 50 entries
        # option = WebDriverWait(driver, 10).until(
        #     EC.ele((By.ID, "list-item-4072-3"))
        # )
        elements = driver.find_elements(By.CSS_SELECTOR, "div[role='option']")
        option = elements[-1]
        option.click()
        print('clicked')
        time.sleep(15)  # Wait for the page to reload with 50 entries

    except Exception as e:
        print(f"Error selecting entries per page: {e}")


def extract_table_data(driver):
    # Wait for the table to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "v-data-table"))
    )

    # Give some extra time for the table to fully render
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "token"))
    )

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the table
    table = soup.find('table')

    if table is None:
        print("Error: Could not find the table on the page")
        return None

    # Extract data from each row
    data = []
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 5:
            document = cells[1].text.strip()
            contexte_avant = cells[2].text.replace('\n', '').strip()
            pivot = cells[3].text.replace('\n', '').strip()
            contexte_apres = cells[4].text.replace('\n', '').strip()

            data.append({
                'document': document,
                'contexte_avant': contexte_avant,
                'pivot': pivot,
                'contexte_apres': contexte_apres
            })
    print(f"{len(data)} occurrences", end='\t')
    return data


def make_excel(dicts, folder, doc_name='doc'):
    doc = [d['document'] for d in dicts]
    cv = [d['contexte_avant'] for d in dicts]
    pv = [d['pivot'] for d in dicts]
    cp = [d['contexte_apres'] for d in dicts]

    data = {"Document": doc,
            "contexte_avant": cv,
            "pivot": pv,
            "contexte_apres": cp}

    tb = pd.DataFrame.from_dict(data)
    tb.fillna('', inplace=True)  # remplace NaN by ''

    cols = ['contexte_avant', 'pivot', 'contexte_apres']
    tb['phrase'] = tb[cols].apply(lambda row: " ".join(row.values.astype(str)), axis=1).str.strip()  # delete white spaces
    tb = tb[['Document', 'pivot', 'phrase']]
    os.makedirs(os.path.join('output', folder), exist_ok=True)
    tb.to_excel(os.path.join('output', folder, f'{doc_name}.xlsx'), index=False)


def click_word(driver, word):
    # Wait for the list of words to be present
    word_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "general-lexicon__container__list-words"))
    )

    # Find all list items within the word list
    list_items = word_list.find_elements(By.TAG_NAME, "li")

    # Iterate through list items to find the one containing "ne"
    for item in list_items:
        link = item.find_element(By.TAG_NAME, "a")
        word_occurrences = link.text.strip().lower()
        occurrences = re.search(r'(\d+)\)', word_occurrences).group(1)
        if re.match(rf'^{word}\s', word_occurrences):
            # Wait for the element to be clickable and then click it
            WebDriverWait(item, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, 'a'))).click()
            print(f"Successfully clicked on {word}")
            return int(occurrences)
    print(f"{word} not found in the list")
    return None


def copy_pages(occurrences, driver):
    data = []

    if occurrences > 10:
        select_entries_per_page(driver)

    page = 1
    last_page = False
    try:
        while not last_page:
            # Extract data from current page
            print(f'processing the Page {page}...', end='\t')
            page_data = extract_table_data(driver)
            data.extend(page_data)
            print(f'Page {page} finished')

            # Try to find and click the "Next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Page suivante']")
                if 'v-btn--disabled' in next_button.get_attribute('class'):
                    print("This is the last page.\nFinished!")
                    break
                next_button.click()
                time.sleep(20)  # Wait for the next page to load
                print('...waiting')
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
            page += 1
    finally:
        # time.sleep(1000)
        driver.quit()

    return data


def navigate(url, word) -> list:
    words_data = []
    driver = setup_driver()
    driver.set_window_size(1280, 800)
    driver.get(url)

    banner_handler(driver)
    occurrences = click_word(driver, word)
    if occurrences is not None:
        time.sleep(10)
        words_data.extend(copy_pages(occurrences, driver))
    return words_data


def candidates():
    with open('documents_link.json', 'r', encoding='utf-8') as f:
        docs_link = json.load(f)
    return {d: l for d, l in docs_link.items() if re.search(r'_9\d\d\w', d) and d not in ignore_cand}


ignore_cand = {'HoMa2012_Céline_906F61'}
dl9 = candidates()
letter = 'p'
words_to_search = ["plus"]
for d, l in dl9.items():
    n = f"https://fdlq.crifuq.usherbrooke.ca{l}?p=1&l={letter}"
    # print(n)
    print(f'Processing {d}')
    dicts = []
    for word in words_to_search:
        dicts.extend(navigate(n, word))
    make_excel(dicts, words_to_search[0], d)
    print('---------------------------------------------------------------\n')
