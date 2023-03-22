from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from config import CHANNEL_ACCESS_TOKEN, USER_ID


# CHANNEL_ACCESS_TOKEN = ''
# USER_ID = ''

def send_message(content: str) -> None:
    """Login to LINE bot API and send text message"""
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=content))
    except LineBotApiError as e:
        print(e.message)


if __name__ == "__main__":
    with open('sample_test.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---')

    instruction = parts[0].strip()
    questions = parts[1].strip()

    send_message(instruction)
    send_message(questions)
