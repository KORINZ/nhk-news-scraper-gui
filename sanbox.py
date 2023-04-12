from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

from main import clear_terminal


def predict_sentiment_jp(text: str, model_name: str = "koheiduck/bert-japanese-finetuned-sentiment") -> dict[str, str]:
    """Predict sentiment of input text using a pre-trained model."""
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Encode input text and return pytorch tensors
    encoded_review = tokenizer(text, return_tensors="pt")

    # Get model output
    output = model(**encoded_review)

    # Calculate softmax scores
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
    clear_terminal()
    print("入力テキスト:")
    print(f"{text}\n")


def print_sentiment_scores(scores_dict: dict[str, str]) -> None:
    """Print sentiment scores."""
    print("感情スコア:")
    for sentiment, score in scores_dict.items():
        print(f"{sentiment}: {score}")
    print()


if __name__ == "__main__":

    text = """なんとなく、以前よりも質が悪くなった気がします。ちょっと拭いただけでボロボロボロとカスがたくさん出るため、メイクでは使いにくい。鼻をかんだだけで、鼻、口まわりにカスがついて、いちいち取るのが面倒。これじゃ敏感肌にいい、保湿とか言われても使う気にならない。前はそんなことなかったのに。。残念です。"""

    print_input_text(text)
    sentiment_scores_dict = predict_sentiment_jp(text)
    print_sentiment_scores(sentiment_scores_dict)
