# Standard library imports
from typing import Dict, List
import os
import sys
import random
import string
from collections import deque
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable

# Third-party imports
import chardet
import locale
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

# Local imports
from send_line_message import send_message
from get_definition import get_definition_list, get_number_of_word, setup_selenium

try:
    from check_sentiment import predict_sentiment_jp, read_news_article
except ImportError:
    pass


"""
NEWS WEB EASY
平日のみ、4つのニュースを更新される
出所の明示でニュースの内容を転載○ 語彙は○ 辞書△×？

https://www.nhk.or.jp/nijiriyou/kyouiku.html
著作権法では、学校その他の教育機関で、授業の教材として複製を認める代わりに、「授業担当者または授業を受ける者が複製すること」や「出所の明示」など、いくつかの条件を守るよう求めています。
また、著作権法が一部改正され、２０２０年４月２８日から、権利者の利益を不当に害しない範囲で、学校の先生や生徒がインターネットなどを通じて、ＮＨＫの番組を教材として利用することが可能になりました。

https://sartras.or.jp/seido/
授業目的公衆送信補償金制度
具体的には、学校等の教育機関の授業で、予習・復習用に教員が他人の著作物を用いて作成した教材を生徒の端末に送信したり、サーバにアップロードしたりすることなど、ICTの活用により授業の過程で利用するために必要な公衆送信について、個別に著作権者等の許諾を得ることなく行うことができるようになります。
"""

# Initial settings and website and file paths
NEWS_HOMEPAGE_URL = "https://www3.nhk.or.jp/news/easy/"
NEWS_ARTICLE_URL_IDENTIFIER = "k1001"
NEWS_ARTICLE_TXT_LOCATION = r"txt_files/news_article.txt"
PRONOUN_QUIZ_LOCATION = r"txt_files/pronunciation_quiz.txt"
DEF_QUIZ_LOCATION = r"txt_files/definition_quiz.txt"
PAST_QUIZ_DATA_LOCATION = r"txt_files/past_quiz_data.txt"
LOG_LOCATION = r"txt_files/push_log.txt"

# Selenium checking settings constants
MAX_URL_CHECKING_ATTEMPTS = 10
MIN_URL_WORD_COUNT = 3

# Set locale to Japanese
if sys.platform.startswith("win32"):
    locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
else:
    locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")


def generate_pronunciation_quiz(
    url: str, word_dict: Dict[str, str], questions=4
) -> None:
    """Generate a pronunciation test for students"""
    today = get_today_date_jp()[1]

    # randomly remove questions until the number of questions reach a desired value
    while len(word_dict) > questions:
        word_dict.pop(random.choice(list(word_dict.keys())))

    # write the test to a file
    with open(PRONOUN_QUIZ_LOCATION, "w", encoding="utf-8") as f:
        f.write(f"【語彙力クイズ】{today}\n\n")
        f.write(
            f"今日読んだNHK EASYニュース📰を復習して、辞書を見ずにスマホで単語・漢字の読み方を書いてください。\n"
            + f"カタカナの場合は日本語もしくは英語で意味を書いてください。({len(word_dict)}ポイント)\n\n"
        )
        f.write(f"{url}\n\n")
        f.write("---\n\n")
        f.write("学生番号: \n\n")
        for i, word in enumerate(word_dict.keys(), start=1):
            letter = string.ascii_uppercase[i - 1]
            f.write(f"{letter}. {word}: \n")


def generate_definition_quiz(
    article, word_dict: Dict[str, str], word_list: List
) -> str:
    """Generate a definition test for students and return the answer key"""
    today = get_today_date_jp()[1]

    # Extract and process questions from the word dictionary
    new_word_list_header = []
    new_word_list = []
    for key in word_dict.keys():
        for definition in word_list:
            if key == definition.split("：", 1)[0]:
                new_word_list_header.append(definition.split("：", 1)[0])
                new_word_list.append(definition.split("：", 1)[1])

    # Shuffle the order of the questions and print the answer key
    new_word_list_header = [
        f"{item}{string.ascii_uppercase[i]}"
        for i, item in enumerate(new_word_list_header)
    ]
    random.shuffle(new_word_list_header)
    answer = "".join([item[-1] for item in new_word_list_header])
    print(f"\n単語意味クイズ解答：{answer}")
    new_word_list_header = [
        f"{item[:-1]} {string.ascii_uppercase[i]}"
        for i, item in enumerate(new_word_list_header)
    ]

    # write the test to a file
    with open(DEF_QUIZ_LOCATION, "w", encoding="utf-8") as f:
        f.write(f"【単語意味クイズ】{today}\n\n")
        f.write(
            f"今日のNHK EASYニュース📰です。(1) から正しい単語の意味を順番に並べてください。({len(new_word_list)}ポイント)\n\n"
        )

        # write the article to a file
        for paragraph in article:
            for p_tag in paragraph.find_all("p"):
                f.write(p_tag.text.strip() + "\n\n")

        f.write("---\n\n")

        for i, word in enumerate(new_word_list_header, start=1):
            f.write(f'({i}) {word.split(" ")[0]} ')

        f.write("\n\n")

        for i, word in enumerate(new_word_list, start=1):
            letter = string.ascii_uppercase[i - 1]
            f.write(f"{letter}. {word}\n\n")

        # write sample answer format
        f.write("【返信フォーマット】(英語アルファベットと数字のみ):\n")
        f.write("学生番号: A10001\n")
        f.write("解答: ABCDE")

        return answer


def get_news_url(driver: webdriver.Chrome) -> str:
    """Retrieve up-to-date news url links"""
    for _ in range(MAX_URL_CHECKING_ATTEMPTS):
        try:
            driver.get(NEWS_HOMEPAGE_URL)
        except WebDriverException:
            raise ConnectionError("インターネットの接続を確認してください。")

        links = driver.find_elements(By.XPATH, "//a[@href]")
        news_links = [
            link.get_attribute("href")
            for link in links
            if NEWS_ARTICLE_URL_IDENTIFIER in link.get_attribute("href")
        ]
        news_current = list(set(news_links[1:9]))

        # Remove links with less than min_word_count
        news_current = [
            link
            for link in news_current
            if get_number_of_word(link)[0] >= MIN_URL_WORD_COUNT
        ]

        # If links are found, return a random link
        if news_current:
            new_url = random.choice(news_current)
            return new_url

    # If no links are found after max_attempts, return None
    error_message = (
        f"{MAX_URL_CHECKING_ATTEMPTS}回の試行後、{MIN_URL_WORD_COUNT}語以上のリンクが見つかりませんでした。"
    )
    with open(LOG_LOCATION, "w", encoding="utf-8") as file:
        file.write(f"{get_today_date_jp()[1]}\n")
        file.write(f"{error_message}")
    raise RuntimeError(error_message)


def write_text_data(content, action="a", location=NEWS_ARTICLE_TXT_LOCATION, encoder="utf-8") -> None:
    """Write text (BeautifulSoup | NavigableString) content to a file"""
    if content is not None:
        with open(location, action, encoding=encoder) as file:
            for p_tag in content.find_all("p"):
                for line in p_tag.get_text().splitlines():
                    stripped_line = line.strip()
                    if stripped_line:
                        file.write(stripped_line + '\n\n')


def is_hiragana_char(character: str) -> bool:
    """Check if a character is hiragana or not"""
    return "\u3040" <= character <= "\u309F"


def get_today_date_jp() -> Tuple:
    """Return today's date in both datetime and Japanese format"""
    now = datetime.now()
    return now, now.strftime(f"%Y年%m月%d日 {get_day_of_week_jp(now)} %H時%M分")


def get_day_of_week_jp(date) -> List:
    """Return day of the week in Japanese"""
    week_list = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    return week_list[date.weekday()]


def save_quiz_vocab(news_url: str) -> None:
    """Save pushed quiz vocabularies and news url to a file"""
    today = get_today_date_jp()[1]
    with open(NEWS_ARTICLE_TXT_LOCATION, "r", encoding="utf-8") as f:
        content = f.read()
        parts = content.split("---")
        vocab = parts[1].strip()
        vocab_def = parts[2].strip()
    with open(PAST_QUIZ_DATA_LOCATION, "a+", encoding="utf-8") as f:
        f.write(f"{today}\n{news_url}\n{vocab}\n\n{vocab_def}\n\n")
        f.write("---\n\n")


def push_quiz(test_type: str, broadcasting=False) -> None:
    """Send message via LINE API to students"""
    with open(test_type, "r", encoding="utf-8") as f:
        content = f.read()
        parts = content.split("---")
        instruction = parts[0].strip()
        questions = parts[1].strip()

    send_message("text", instruction, broadcasting=broadcasting)
    send_message("text", questions, broadcasting=broadcasting)


def log_sentiment_score() -> Dict[str, str]:
    """Get the sentiment score of the text."""
    article = read_news_article()
    score_dict = predict_sentiment_jp(article)
    return score_dict


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main(
    quiz_type: str,
    push=False,
    broadcasting=False,
    questions=5,
    progress_callback: Optional[Callable] = None,
) -> None:
    """Establish request connection and randomly scrap a Japanese news article's content and vocabularies"""
    # Get and encode a random news url; parsing the HTML content
    driver = setup_selenium()
    url = get_news_url(driver)

    # Get the article vocabularies and definitions
    definition_list = get_definition_list(driver, url, progress_callback)
    driver.close()

    # Establish a request connection to the url
    response = requests.get(url)
    encoding = chardet.detect(response.content)["encoding"]
    response.encoding = encoding
    if response.status_code == 200:
        # HTTP status OK
        html_content = response.text
    else:
        sys.exit("Request failed. Check your Internet connection.")
    soup = BeautifulSoup(html_content, "html.parser")

    # Article url (アドレス)
    with open(NEWS_ARTICLE_TXT_LOCATION, "w") as f:
        f.write(f"{url}\n\n")

    # Article publishing date (掲載日)
    date = soup.find("p", class_="article-main__date")
    write_text_data(date)

    # Article title (タイトル)
    title = soup.find("h1", class_="article-main__title")
    write_text_data(title)

    # Article content (内容)
    article = soup.find_all("div", class_="article-main__body article-body")
    for paragraph in article:
        write_text_data(paragraph)

    # Important vocabularies (語彙)
    vocabulary_list = soup.find_all("a", class_="dicWin")
    vocabulary_dict = {}
    furigana = ""

    # Create a dictionary of vocabulary: furigana
    for vocabulary in vocabulary_list:
        word = vocabulary.text
        rt = vocabulary.find_all("rt")

        if rt:
            for i, _ in enumerate(rt):
                curr = rt[i].text
                if i > 0:
                    furigana += " " + curr
                else:
                    furigana = curr

        else:
            # If keys are カタカナ, give them empty string as values instead
            furigana = ""

        vocabulary_dict[word] = furigana

    # Reformat word: 話し合う: はな あ -> 話(はな)し合(あ)う
    formatted_word_list = []
    for key, value in vocabulary_dict.items():
        word = ""
        combine = False
        for char in key:
            if is_hiragana_char(char):
                combine = True

        # If the word is a combination of hiragana, combine the furigana
        if combine:
            key += " "
            kana = deque(value.split(" "))
            for i, char in enumerate(key):
                if (
                    not is_hiragana_char(char)
                    and (i + 1 < len(key))
                    and (is_hiragana_char(key[i + 1]) or " ")
                ):
                    try:
                        word += f"{char}({kana[0]})"
                        kana.popleft()
                    except IndexError:
                        word += char
                        word = word.replace(f"({value})", "")
                else:
                    word += char
        if word:
            word = word.replace(" ", "")
            formatted_word_list.append(word)
        else:
            formatted_word = f"{key}({value})"
            if "()" in formatted_word:
                formatted_word = formatted_word.replace("()", "")
            formatted_word_list.append(formatted_word)

    # Write formatted vocabularies to a file
    with open(NEWS_ARTICLE_TXT_LOCATION, "a", encoding="utf-8") as f:
        f.write("---\n")
        for word in formatted_word_list:
            f.write(f"\n{word}")

    # Printing news title, date, and url
    if title and date:
        print(f"\n{title.text.strip()} {date.text}")
        print(f"{url}\n")

    # Modify the definition list to include the original word; get current progress

    definition_list_original_word = []
    for key, meaning in zip(vocabulary_dict.keys(), definition_list):
        try:
            definition_list_original_word.append(
                key + "：" + meaning.split("：", 1)[1])
        except IndexError:
            print(
                f"\nWARNING: definition_list is missing a or some element(s). This is a rare case due to incomplete scrapping of selenium. Consider re-running the program or change the scale for document.body.style.transform in get_definition.py."
            )
            pass

    # Save definitions to a news_article.txt file
    with open(NEWS_ARTICLE_TXT_LOCATION, "a", encoding="utf-8") as f:
        f.write("\n\n---\n\n")
        for definition in definition_list_original_word:
            f.write(f"{definition}\n")

    # Generate the pronunciation quiz
    generate_pronunciation_quiz(url, vocabulary_dict, questions=questions)

    # Get the answer to the definition quiz and generate the definition quiz
    def_answer = generate_definition_quiz(
        article, vocabulary_dict, definition_list_original_word
    )

    # Save quiz sent time and news url to a log file
    with open(LOG_LOCATION, "w", encoding="utf-8") as f:
        now = get_today_date_jp()[0]
        now = now.strftime(f"%Y-%m-%d %H:%M:%S")
        f.write(f"{now}\n{url}\n単語意味クイズ解答：{def_answer}\n")
        try:
            scores_dict = log_sentiment_score()
            for sentiment, score in scores_dict.items():
                f.write(f"{sentiment}: {score}\n")
        except NameError:
            print("Sentiment analysis module failed. Skipping sentiment analysis.")

    # Push quiz to LINE if push is True
    if push:
        if quiz_type == "単語意味クイズ":
            push_quiz(DEF_QUIZ_LOCATION, broadcasting=broadcasting)
            save_quiz_vocab(url)
        elif quiz_type == "読み方クイズ":
            push_quiz(PRONOUN_QUIZ_LOCATION, broadcasting=broadcasting)
            save_quiz_vocab(url)

        # Save quiz sent time and news url to a log file
        with open(LOG_LOCATION, "a", encoding="utf-8") as f:
            f.write("送信済み\n")


if __name__ == "__main__":
    # Clearing the terminal
    clear_terminal()

    # quiz_type: '単語意味クイズ' or '読み方クイズ'
    main(quiz_type="単語意味クイズ", push=False, broadcasting=False, questions=5)
