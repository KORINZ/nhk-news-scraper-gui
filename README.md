# NHK News Web Easy Scraper

### CustomTkinter Version GUI v1.9.3
<p align="center">
  <img width="800" alt="1" src="https://user-images.githubusercontent.com/111611023/230731185-6988b3ff-4ddd-456f-81e8-8db396819552.gif">
</p>

### Tkinter Version GUI v1.0.0 (deprecated)
<p align="center">
  <img width="800" alt="1" src="https://user-images.githubusercontent.com/111611023/228608713-99dcb154-2abb-4f53-93bf-d437506e0d60.gif">
</p>

This project is a Python script for scraping news articles from [NHK News Web Easy](https://www3.nhk.or.jp/news/easy/),
a website that provides news articles written in simpler Japanese, suitable for language learners.
The script extracts the article's URL, title, content, and important vocabularies along with their furigana (hiragana reading) and generate a quiz for students based on the scraped article.

See the `.txt` file in the repository for an example output.

## Features

- Extract a random news article from NHK News Web Easy
- Save article details (URL, date, title, content) and featured vocabularies (with furigana) in a text file
- Generate a daily quiz for students based on the scraped article
- Send customized text or sticker messages from a terminal interface
- Generate quizzes and send them via LINE with GUI
- Automatically receive (via Google Apps Script) and evaluate answers and upload them to Google Sheets

## Dependencies

- `Python 3`
- `chardet`
- `BeautifulSoup4`
- `Selenium`
- `requests`
- `line-bot-sdk`
- `pandas`
- `gspread`
- `tabulate`
- `customtkinter`

## Installation

1. Sign up for a [LINE official account](https://www.linebiz.com/jp/signup/).
2. Get your own `CHANNEL_ACCESS_TOKEN` and `USER_ID` from [LINE Developers](https://developers.line.biz/ja/) Messaging API Settings.
3. Install the required packages listed in the dependencies:

```bash
pip install -r requirements.txt
```

4. Clone this repository:

```bash
git clone https://github.com/KORINZ/nhk_news_web_easy_scraper.git
```

## Usage

1. To use GUI:

```bash
python customtkinter_GUI.py
```

2. To use on terminal:

```bash
python main.py
```

3. The script will generate a text file news_article.txt containing the article's URL, date, title, content,
and important vocabularies (with furigana) for a random news article.

## GUI User Guide (ユーザーガイド)

- Pending

## Future Work

- Create a database to store all past news articles, vocabularies, and quizzes
- Improve the formatting of the output text file
- Add more customization options, such as selecting specific news categories or timeframes

## Disclaimer

Note that this script is for educational purposes only. When using the scraped content, follow the copyright laws and regulations applicable in your country.
Make sure to properly cite the source of the content and respect the intellectual property rights of the content owners.
