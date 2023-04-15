import deepl

from config import DEEPL_API_KEY
from check_sentiment import read_news_article

# TODO: translate Japanese vocabularies to Swedish and make a quiz

translator = deepl.Translator(DEEPL_API_KEY)

text = read_news_article()
print(text)

results = translator.translate_text(
    text, target_lang="SV")  # Swedish (SV)

# Ensure that 'results' is always a list
if not isinstance(results, list):
    results = [results]

for result in results:
    print(result.text)
