import deepl
import argparse
import sys

from config import DEEPL_API_KEY
from check_sentiment import read_news_article

# TODO: translate Japanese vocabularies to Swedish and make a quiz

NEWS_ARTICLE_LOCATION = r"txt_files/news_article.txt"
translator = deepl.Translator(DEEPL_API_KEY)


def get_article() -> str:
    with open(NEWS_ARTICLE_LOCATION, 'r', encoding='utf-8') as file:
        content = file.read()
        parts = content.split("---")
        main_article = parts[0]
        lines = main_article.split('\n')
        main_article = '\n'.join(lines[1:])
        return main_article


def get_vocabularies() -> str:
    with open(NEWS_ARTICLE_LOCATION, 'r', encoding='utf-8') as file:
        content = file.read()
        parts = content.split("---")
        vocabularies = parts[2].strip().split("\n")
        vocabularies = [item.split("：")[0] for item in vocabularies]
        vocabularies = '\n'.join(vocabularies)
        return vocabularies


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate text from one language to another")
    parser.add_argument("-t", "--text", type=str,
                        help="text to translate", dest="input_text")
    parser.add_argument("target", type=str, default=None, nargs='?',
                        help="target language (optional when using -l)")
    parser.add_argument("-f", "--file", type=str,
                        default=None, help="file to translate")
    parser.add_argument("-a", "--article", action='store_true',
                        help="use predefined article")
    parser.add_argument("-p", "--pair", action='store_true',
                        help="use predefined article and vocabularies")
    parser.add_argument("-s", "--source", type=str, default=None,
                        help="source language (optional)")
    parser.add_argument("-u", "--usage", action='store_true',
                        help="show account usage")
    parser.add_argument("-l", "--list", action='store_true',
                        help="list all languages abbreviations")
    args = parser.parse_args()

    if args.input_text:
        input_text = args.input_text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as file:
            input_text = file.read()
            print(f"{input_text}\n")
    elif args.article:
        input_text = get_article()
    elif args.pair:
        with open(NEWS_ARTICLE_LOCATION, 'r', encoding='utf-8') as file:
            input_text = get_vocabularies()
    elif args.list:
        for language in translator.get_source_languages():
            print(f"{language.name} ({language.code})")
        sys.exit(0)
    elif args.usage:
        usage = translator.get_usage()
        if usage.character.valid:
            print(
                f"Character usage: {usage.character.count} of {usage.character.limit}")
        if usage.document.valid:
            print(
                f"Document usage: {usage.document.count} of {usage.document.limit}")
        sys.exit(0)
    else:
        print("Please specify either a text or a file to translate")
        return

    target_lang = args.target
    source_lang = args.source

    results = translator.translate_text(
        input_text, target_lang=target_lang, source_lang=source_lang)  # Swedish (SV)

    # Ensure that 'results' is always a list
    if not isinstance(results, list):
        results = [results]

    if args.pair:
        input_text = input_text.split('\n')
        results = [result.text for result in results][0].split('\n')
        for source, result in zip(input_text, results):
            print(f"{source}: {result.lower()}")
    elif args.article:
        print(input_text)
        for result in results:
            print(result.text)
    else:
        for result in results:
            print(result.text)


if __name__ == "__main__":
    main()
