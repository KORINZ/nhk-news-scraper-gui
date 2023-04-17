# Standard library imports
import sys
import re
from time import sleep
from typing import List, Tuple, Optional, Callable

# Third-party imports
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

PATTERN = re.compile(r"^RSHOK-")


def setup_selenium_webdriver() -> webdriver.Chrome:
    """Setup selenium webdriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if sys.platform.startswith("win32"):
        from selenium.webdriver.chrome.service import Service as ChromeService
        from subprocess import CREATE_NO_WINDOW  # type: ignore

        chrome_service = ChromeService("chromedriver")
        chrome_service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=options, service=chrome_service)
    else:
        driver = webdriver.Chrome(options=options)

    return driver


def get_number_of_word(url: str) -> Tuple[int, List, BeautifulSoup]:
    """Get number of words from the given url."""
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        sys.exit("Connection error. Please check your internet connection.")
    response.encoding = response.apparent_encoding
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    matching_ids = list(
        dict.fromkeys([element["id"] for element in soup.find_all(id=PATTERN)])
    )
    return len(matching_ids), matching_ids, soup


def get_definition_list(
    driver: webdriver.Chrome, url: str, progress_callback: Optional[Callable] = None
) -> List[str]:
    """Get definition list from the given url."""
    matching_ids = get_number_of_word(url)[1]
    driver.get(url)
    button = driver.find_element(By.CLASS_NAME, "easy-wrapper")
    driver.execute_script(
        "arguments[0].setAttribute('class', 'easy-wrapper is-no-ruby')", button
    )
    driver.execute_script("document.body.style.transform='scale(0.99)';")

    definition_list = []
    total_ids = len(matching_ids)
    sleep(0.2)
    for index, matching_id in enumerate(matching_ids, start=1):
        element_to_hover_over = driver.find_element(By.ID, matching_id)
        hover = ActionChains(driver).move_to_element(element_to_hover_over)
        hover.perform()

        dictionary_box = driver.find_element(
            By.CSS_SELECTOR, ".dictionary-box")

        text_content = dictionary_box.text
        text_content = "".join(text_content.split())
        text_content = text_content.replace("1", "： 1", 1)
        print(text_content)
        definition_list.append(text_content)
        if progress_callback:
            progress = index / total_ids
            progress_callback(progress, index, total_ids)

    return definition_list


if __name__ == "__main__":
    test_url = "https://www3.nhk.or.jp/news/easy/k10014030681000/k10014030681000.html"
    driver = setup_selenium_webdriver()
    definition_list = get_definition_list(driver, test_url)
    driver.close()
