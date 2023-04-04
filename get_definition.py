from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Callable

import requests
import re
import sys

# Regular expression to match word ids which contain RSHOK- prefix
PATTERN = re.compile(r'^RSHOK-')


def get_number_of_word(url: str) -> Tuple[int, List, BeautifulSoup]:
    """Get number of words and word ids which contain RSHOK- prefix"""
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        sys.exit('Connection error. Please check your internet connection.')
    response.encoding = response.apparent_encoding
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    matching_ids = list(dict.fromkeys([element['id']
                                       for element in soup.find_all(id=PATTERN)]))
    return len(matching_ids), matching_ids, soup


def get_definition_list(url: str, progress_callback: Optional[Callable] = None) -> List[str]:
    """Get definition list of words which contain RSHOK-K- prefix"""
    # Get word ids which contain RSHOK- prefix
    matching_ids = get_number_of_word(url)[1]

    # Selenium setup
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Turn off furigana and transform scale
    button = driver.find_element(By.CLASS_NAME, "easy-wrapper")
    driver.execute_script(
        "arguments[0].setAttribute('class', 'easy-wrapper is-no-ruby')", button)
    driver.execute_script("document.body.style.transform='scale(0.99)';")

    definition_list = []
    # Hover over each word and print definition
    total_ids = len(matching_ids)
    for index, matching_id in enumerate(matching_ids, start=1):
        element_to_hover_over = driver.find_element(By.ID, matching_id)
        hover = ActionChains(driver).move_to_element(element_to_hover_over)
        hover.perform()

        # Get definition
        dictionary_box = driver.find_element(
            By.CSS_SELECTOR, ".dictionary-box")

        # Remove unnecessary characters
        text_content = dictionary_box.text
        text_content = ''.join(text_content.split())
        text_content = text_content.replace('1', '： 1', 1)
        print(text_content)
        definition_list.append(text_content)
        # Update the progress bar
        if progress_callback:
            progress = index / total_ids
            progress_callback(progress, index, total_ids)

    return definition_list


if __name__ == '__main__':
    test_url = 'https://www3.nhk.or.jp/news/easy/k10014023731000/k10014023731000.html'
    definition_list = get_definition_list(test_url)
