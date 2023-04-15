import deepl
from config import DEEPL_API_KEY

translator = deepl.Translator(DEEPL_API_KEY)

text = """こんにちは。私は日本語が話せます。"""

result = translator.translate_text(text, target_lang="SV")  # Swedish (SV)
translated_text = result.text

print(translated_text)
