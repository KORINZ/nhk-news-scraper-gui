# NHK News Web Easy Scraper

This project is a Python script for scraping news articles from [NHK News Web Easy](https://www3.nhk.or.jp/news/easy/),
a website that provides news articles written in simpler Japanese, suitable for language learners.
The script extracts the article's URL, title, content, and important vocabularies along with their furigana (hiragana reading) and generate a quiz for students based on the scraped article.

See the `.txt` file in the repository for an example output.

## Features

- Extract a random news article from NHK News Web Easy
- Save article details (URL, date, title, content) and featured vocabularies (with furigana) in a text file
- Generate a daily quiz for students based on the scraped article

## Dependencies

- `Python 3`
- `BeautifulSoup4`
- `Selenium`
- `requests`
- `line-bot-sdk`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/KORINZ/nhk_news_web_easy_scraper.git
```

1. Install the required packages listed in the dependencies.

## Usage

1. Run the script:

```bash
python main.py
```

1. The script will generate a text file news_article.txt containing the article's URL, date, title, content,
and important vocabularies (with furigana) for a random news article.

## Future Work

- Create a database to store all past news articles, vocabularies, and quizzes
- Improve the formatting of the output text file
- Add more customization options, such as selecting specific news categories or timeframes

## Disclaimer

Note that this script is for educational purposes only. When using the scraped content, follow the copyright laws and regulations applicable in your country.
Make sure to properly cite the source of the content and respect the intellectual property rights of the content owners.
