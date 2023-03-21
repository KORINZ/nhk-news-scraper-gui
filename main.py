import datetime
import locale
import requests
import random
import sys
import os

from bs4 import BeautifulSoup
from collections import deque
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Dict

'''
NEWS WEB EASY
平日のみ、4つのニュースを更新される
更新時間は日本時間夜以降
まとめて4つのニュース更新される
出所の明示でニュースの内容を転載○ 語彙は○ 辞書△×？

https://www.nhk.or.jp/nijiriyou/kyouiku.html
著作権法では、学校その他の教育機関で、授業の教材として複製を認める代わりに、「授業担当者または授業を受ける者が複製すること」や「出所の明示」など、
いくつかの条件を守るよう求めています。
また、著作権法が一部改正され、２０２０年４月２８日から、権利者の利益を不当に害しない範囲で、学校の先生や生徒がインターネットなどを通じて、
ＮＨＫの番組を教材として利用することが可能になりました。

https://sartras.or.jp/seido/
授業目的公衆送信補償金制度
具体的には、学校等の教育機関の授業で、予習・復習用に教員が他人の著作物を用いて作成した教材を生徒の端末に送信したり、
サーバにアップロードしたりすることなど、ICTの活用により授業の過程で利用するために必要な公衆送信について、
個別に著作権者等の許諾を得ることなく行うことができるようになります。
'''

# Initial settings and website and file paths
sys.setrecursionlimit(50)
locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
PATH = 'https://www3.nhk.or.jp/news/easy/'
NEWS_ARTICLE_IDENTIFIER = 'k1001'
TXT_FILE_LOCATION = r'./news_article.txt'
EXAM_FILE_LOCATION = r'./sample_test.txt'


def get_news_url() -> str:
    """Retrieve up-to-date news url links"""
    opt = webdriver.ChromeOptions()
    opt.add_argument('headless')
    driver = webdriver.Chrome(options=opt)
    driver.get(PATH)

    links = driver.find_elements(By.XPATH, "//a[@href]")
    news_links = [link.get_attribute("href")
                  for link in links if NEWS_ARTICLE_IDENTIFIER in link.get_attribute("href")]
    news_current = list(set(news_links[1:9]))

    try:
        new_url = random.choice(news_current)
    except IndexError:
        return get_news_url()
    return new_url


def write_text_data(content, action='a', location=TXT_FILE_LOCATION, encoder='utf-8') -> None:
    """Write text (BeautifulSoup | NavigableString) content to a file"""
    if content is not None:
        with open(location, action, encoding=encoder) as file:
            file.write(content.text.strip() + '\n\n')


def is_hiragana_char(character: str) -> bool:
    """Check if a character is hiragana or not"""
    return u'\u3040' <= character <= u'\u309F'


def generate_quiz(word_dict: Dict[str, str]) -> None:
    """Generate a test for students"""
    dt_now = datetime.datetime.now().strftime('%Y年%m月%d日 %H時%M分')
    with open(EXAM_FILE_LOCATION, 'w', encoding='utf-8') as f:
        f.write(f'語彙力クイズ {dt_now}\n\n')
        f.write(f'今日読んだニュースを復習して、辞書を見せずにスマホで簡単な日本語で単語・漢字の読み方と意味を書いてください。\n' +
                f'カタカナは意味のみ書いてください。難しい場合は英語でもいいです。({len(word_dict)}ポイント)\n\n')
        f.write('お名前: \n学生番号: \n\n')
    for i, word in enumerate(word_dict.keys(), start=1):
        with open(EXAM_FILE_LOCATION, 'a', encoding='utf-8') as f:
            f.write(f'{i}. {word}: \n')


def main() -> None:
    # Get and encode a random news url; parsing the HTML content
    url = get_news_url()
    response = requests.get(url)
    response.encoding = response.apparent_encoding

    if response.status_code == 200:
        # HTTP status OK
        html_content = response.text
    else:
        print('Request failed. Check your Internet connection.')
        sys.exit()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Article url (アドレス)
    with open(TXT_FILE_LOCATION, 'w') as f:
        f.write(f'{url}\n\n')

    # Article publishing date (掲載日)
    date = soup.find('p', class_='article-main__date')
    write_text_data(date)

    # Article title (タイトル)
    title = soup.find('h1', class_='article-main__title')
    write_text_data(title)

    # Article content (内容)
    article = soup.find_all('div', class_='article-main__body article-body')
    for paragraph in article:
        write_text_data(paragraph)

    # Important vocabularies (語彙)
    vocabulary_list = soup.find_all('a', class_='dicWin')
    vocabulary_dict = {}
    furigana = ''

    for vocabulary in vocabulary_list:
        word = vocabulary.text
        rt = vocabulary.find_all('rt')

        if rt:
            for i, _ in enumerate(rt):
                curr = rt[i].text
                if i > 0:
                    furigana += ' ' + curr
                else:
                    furigana = curr

        else:
            # If keys are カタカナ, give them empty string as values instead
            furigana = ''

        vocabulary_dict[word] = furigana

    for key, value in vocabulary_dict.items():
        with open(TXT_FILE_LOCATION, 'a', encoding='utf-8') as f:
            f.write(f'{key}: {value}\n')

    # Reformat word: 話し合う: はな あ -> 話(はな)し合(あ)う
    formatted_word_list = []

    for key, value in vocabulary_dict.items():
        word = ''
        combine = False
        for char in key:
            if is_hiragana_char(char):
                combine = True

        if combine:
            kana = deque(value.split(' '))
            for char in key:
                if not is_hiragana_char(char):
                    word += f'{char}({kana[0]})'
                    kana.popleft()
                else:
                    word += char
        if word:
            formatted_word_list.append(word)
        else:
            formatted_word = f'{key}({value})'
            if '()' in formatted_word:
                formatted_word = formatted_word.replace('()', '')
            formatted_word_list.append(formatted_word)

    for word in formatted_word_list:
        with open(TXT_FILE_LOCATION, 'a', encoding='utf-8') as f:
            f.write(f'\n{word}')

    generate_quiz(vocabulary_dict)

    # Printing news title, date, and url
    if title and date is not None:
        print(f'{title.text.rstrip()} {date.text}')
        print(f'{url}\n')

    # TODO: database for all past news and tests


if __name__ == '__main__':
    # Linux
    if sys.platform.startswith('linux'):
        os.system('clear')
    # Windows
    elif sys.platform.startswith('win32'):
        os.system('cls')
    main()
