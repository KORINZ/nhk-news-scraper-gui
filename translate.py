# Standard library imports
import os
import sys
import argparse
from contextlib import contextmanager
import io

# Third-party imports
import deepl

# Local imports
try:
    from config import DEEPL_API_KEY
except ImportError:
    print(
        "Please create a config.py file in the same directory and have a variable DEEPL_API_KEY"
    )
    sys.exit(1)

# Setup
NEWS_ARTICLE_LOCATION = r"txt_files/news_article.txt"
translator = deepl.Translator(DEEPL_API_KEY)

@contextmanager
def redirect_stdout(encoding):
    old_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, newline='')
    yield
    sys.stdout = old_stdout

def get_news_article() -> str:
    """Get main article from the news article"""
    with open(NEWS_ARTICLE_LOCATION, "r", encoding="utf-8") as file:
        content = file.read()
        parts = content.split("---")
        main_article = parts[0]
        lines = main_article.split("\n")
        main_article = "\n".join(lines[1:])
        return main_article


def get_news_vocabularies() -> str:
    """Get vocabularies from the news article"""
    with open(NEWS_ARTICLE_LOCATION, "r", encoding="utf-8") as file:
        content = file.read()
        parts = content.split("---")
        vocabularies = parts[2].strip().split("\n")
        vocabularies = [item.split("：")[0] for item in vocabularies]
        vocabularies = "\n".join(vocabularies)
        return vocabularies


def translate_document(input_path: str, output_path: str, target_lang: str) -> None:
    """Translate document"""
    try:
        # Using translate_document_from_filepath() with file paths
        translator.translate_document_from_filepath(
            input_path,
            output_path,
            target_lang=target_lang,
        )

    except deepl.DocumentTranslationException as error:
        # If an error occurs during document translation after the document was
        # already uploaded, a DocumentTranslationException is raised.
        doc_id = error.document_handle.id
        doc_key = error.document_handle.key
        print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
    except deepl.DeepLException as error:
        # Errors during upload raise a DeepLException
        print(error)


def show_account_usage() -> None:
    """Show account usage"""
    usage = translator.get_usage()

    character_count = usage.character.count
    character_limit = usage.character.limit

    if usage.any_limit_reached:
        print("Translation limit reached.")
    if (
        usage.character.valid
        and character_count is not None
        and character_limit is not None
    ):
        print(
            f"Character usage: {character_count} of {character_limit} "
            f"({round(character_count / character_limit * 100, 2)}%)"
        )
    if usage.document.valid:
        print(
            f"Document usage: {usage.document.count} of {usage.document.limit}")


def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Translate text/file from one language to another"
    )
    parser.add_argument(
        "target",
        type=str,
        default=None,
        nargs="?",
        help="target language (optional when using -l)",
    )
    parser.add_argument(
        "-t", "--text", type=str, help="text to translate", dest="input_text"
    )
    parser.add_argument(
        "-f", "--file", type=str, default=None, help="txt file to translate"
    )
    parser.add_argument(
        "-d",
        "--document",
        type=str,
        default=None,
        help="translate document (.pdf, .docx, .pptx)",
    )
    parser.add_argument(
        "-a", "--article", action="store_true", help="use predefined article"
    )
    parser.add_argument(
        "-v",
        "--vocab",
        action="store_true",
        help="use predefined article and vocabularies",
    )
    parser.add_argument(
        "-s", "--source", type=str, default=None, help="source language (optional)"
    )
    parser.add_argument("-u", "--usage", action="store_true",
                        help="show account usage")
    parser.add_argument(
        "-l", "--list", action="store_true", help="list all languages abbreviations"
    )

    args = parser.parse_args()
    target_language = args.target
    source_language = args.source

    if args.input_text:
        input_text = args.input_text
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as file:
            input_text = file.read()
            print(f"{input_text}\n")
    elif args.document:
        input_path = args.document
        filename, extension = os.path.splitext(input_path)

        output_path = f"{filename}_translated{extension}"
        translate_document(input_path, output_path, target_language)
        return None

    elif args.article:
        input_text = get_news_article()
    elif args.vocab:
        with open(NEWS_ARTICLE_LOCATION, "r", encoding="utf-8"):
            input_text = get_news_vocabularies()
    elif args.list:
        for language in translator.get_source_languages():
            print(f"{language.name} ({language.code})")
        return None
    elif args.usage:
        show_account_usage()
        return None
    else:
        print("Please specify either a text or a file to translate")
        return None

    results = translator.translate_text(
        input_text, target_lang=target_language, source_lang=source_language
    )

    # Ensure that 'results' is always a list
    if not isinstance(results, list):
        results = [results]

    if args.vocab:
        input_text = input_text.split("\n")
        results = [result.text for result in results][0].split("\n")
        for source, result in zip(input_text, results):
            print(f"{source}: {result.lower()}")
    elif args.article:
        print(input_text)
        for result in results:
            print(result.text)
    else:
        for result in results:
            print(result.text)


if __name__ == '__main__':
    with redirect_stdout('utf-8'):
        main()
