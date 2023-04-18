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
The script extracts the article's URL, title, content, and essential vocabulary along with their furigana (hiragana reading) and generates a quiz for students based on the scraped article.

See the `.txt` file in the repository for an example output.

## Features

- Extract a random news article from NHK News Web Easy
- Save article details (URL, date, title, content) and featured vocabularies (with furigana) in a text file
- Generate a daily quiz for students based on the scraped article
- Send customized quizzes, messages or stickers to LINE with Python GUI
- Automatically receive (via Google Apps Script) and evaluate answers and upload them to Google Sheets (via Python)
- Check sentiment scores for the news article
- Translate news articles/vocabularies to other languages via DeepL API with command line interface

## Dependencies

Tested on Python 3.11 with Windows 11, WSL (Ubuntu 20.04), and macOS Ventura.

- `chardet`
- `BeautifulSoup4`
- `Selenium`
- `webdriver_manager`
- `requests`
- `line-bot-sdk`
- `pandas`
- `gspread`
- `tabulate`
- `customtkinter`

Optional:

- `transformers`
- `scipy`
- `torch`
- `torchvision`
- `torchaudio`
- `fugashi[unidic]`
- `ipadic`
- `deepl`

Note: Currently, `fugashi` will not work on Python downloaded from Microsoft Store. You will need to install Python from the official website if you wan to use sentiment analysis.

## Installation

1. Sign up for a [LINE official account](https://www.linebiz.com/jp/signup/).
2. Get your own `CHANNEL_ACCESS_TOKEN` (チャネルアクセストークン) and `USER_ID` (あなたのユーザーID) from [LINE Developers](https://developers.line.biz/ja/) Messaging API Settings.
3. For macOS, installation of MeCab is required if you want to use sentiment analysis:

```bash
brew install mecab
```

4. Clone this repository:

```bash
git clone https://github.com/KORINZ/nhk_news_web_easy_scraper.git
```

5. Install the required packages listed in the dependencies (make sure you are inside the cloned repository folder):

```bash
pip install -r requirements.txt
```

## Terminal Usage (Windows and macOS)

1. To run GUI:

```bash
python customtkinter_GUI.py
```

2. To run on the terminal:

```bash
python main.py
```

3. The script will generate a text file news_article.txt containing the article's URL, date, title, content,
and essential vocabulary (with furigana) for a random news article.

## GUI for WSL (Windows Subsystem for Linux)

1. Install Japanese fonts:

```bash
sudo apt update
sudo apt install -y fonts-ipafont
```

2. Install tkinter; replace `xx` with your Python version:

```bash
sudo apt-get install python3.xx-tk
```

3. Install support for Linux GUI apps, see:

<https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps>

## GUI User Guide (ユーザーガイド)

- Click on `クイズ作成` to scrap a random news article and generate quizzes.
- Click on `LINE機密情報入力` to fill in your `CHANNEL_ACCESS_TOKEN` (チャネルアクセストークン) and `USER_ID` (あなたのユーザーID).
- Click on `LINEに発信` to send the quiz.
- pending

## Grade Book User Guide

- pending

## Translation User Guide

- pending

## Future Work

- Create a database to store all past news articles, vocabularies, and quizzes
- Improve the formatting of the output text file
- Add translation to quiz vocabulary

## Disclaimer

Note that this script is for educational purposes only. When using the scraped content, follow the copyright laws and regulations applicable in your country.
Make sure to properly cite the content's source and respect the content owners' intellectual property rights.
