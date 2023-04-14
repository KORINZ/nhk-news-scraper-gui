from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax


NEWS_ARTICLE_LOCATION = r"txt_files\news_article.txt"
LOG_LOCATION = r"./txt_files/push_log.txt"


def predict_sentiment_jp(text: str, model_name: str = "koheiduck/bert-japanese-finetuned-sentiment") -> dict[str, str]:
    """Predict sentiment of input text using a pre-trained model."""
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Encode input text and return pytorch tensors
    encoded_review = tokenizer(text, return_tensors="pt")

    # Get model output
    output = model(**encoded_review)

    # Get sentiment scores in numpy array and apply softmax function
    scores = output.logits[0].detach().numpy()
    scores = softmax(scores)

    # Format scores as percentages
    scores_str = [str(round(num * 100, 1)) + "%" for num in scores]

    # Create a dictionary of sentiment labels and their respective scores
    scores_dict = {"否定的": scores_str[1],
                   "中立的": scores_str[0], "肯定的": scores_str[2]}

    return scores_dict


def print_input_text(text: str) -> None:
    """Print input text."""
    print("入力テキスト:")
    print(f"{text}\n")


def print_sentiment_scores(scores_dict: dict[str, str]) -> None:
    """Print sentiment scores with a bar graph."""
    print("感情スコア:")
    max_bar_length = 30
    for sentiment, score in scores_dict.items():
        score_percentage = float(score.strip("%"))
        if score_percentage >= 1:
            bar_length = int(score_percentage / 100 * max_bar_length)
            bar = "#" * bar_length
        else:
            bar = ""

        # Adjust the spacing for proper alignment
        formatted_score = f"{score: <5}"
        print(f"{sentiment}: {formatted_score} {bar}")
    print()


def read_news_article() -> str:
    """Read the news article from the txt file"""
    with open(NEWS_ARTICLE_LOCATION, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # Filter out empty lines
        non_empty_lines = [line for line in lines if line.strip()]
        content = "".join(non_empty_lines[1:])  # Exclude the first line (url)
        parts = content.split("---")
        article = parts[0]
    return article


if __name__ == "__main__":

    input_text = read_news_article()
    print_input_text(input_text)

    sentiment_scores_dict = predict_sentiment_jp(input_text)
    print_sentiment_scores(sentiment_scores_dict)
