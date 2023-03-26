from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
from typing import List
import requests
import re


def get_definition_list(url: str, soup) -> List:

    # Get word ids which contain RSHOK-K- prefix
    pattern = re.compile(r'^RSHOK-K-')
    matching_ids = list(dict.fromkeys([element['id']
                        for element in soup.find_all(id=pattern)]))

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
    driver.execute_script("document.body.style.transform='scale(1)';")

    definition_list = []
    # Hover over each word and print definition
    for matching_id in matching_ids:
        element_to_hover_over = driver.find_element(By.ID, matching_id)
        hover = ActionChains(driver).move_to_element(element_to_hover_over)
        hover.perform()

        dictionary_box = driver.find_element(
            By.CSS_SELECTOR, ".dictionary-box")

        text_content = dictionary_box.text
        text_content = ''.join(text_content.split())
        text_content = text_content.replace('1', '： 1', 1)
        print(text_content)
        definition_list.append(text_content)

    return definition_list


if __name__ == '__main__':

    url = 'https://www3.nhk.or.jp/news/easy/k10014015941000/k10014015941000.html'
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    definition_list = get_definition_list(url, soup)