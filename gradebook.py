import gspread
import pandas as pd

from datetime import datetime
from pathlib import Path

LINE_INCOMING_MESSAGE_FILENAME = 'LINE_Messages'
GRADE_BOOK_FILENAME = '日本語ニュース成績表'

now = datetime.now()

sa = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")

# Get quiz start/sent time
with open('log.txt', 'r') as f:
    quiz_start_time = f.readline().strip('\n').split('.')[0]
    datetime.strptime(quiz_start_time, '%Y-%m-%d %H:%M:%S')
    print(quiz_start_time)

line_message = sa.open(LINE_INCOMING_MESSAGE_FILENAME)
message_sheet = line_message.worksheet('Messages')
message_records = message_sheet.get_all_records()
df_message = pd.DataFrame(message_records)
df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])


grade_book = sa.open(GRADE_BOOK_FILENAME)
grade_sheet = grade_book.worksheet('シート1')

if __name__ == "__main__":
    df_message.query('`Sent Time` < @quiz_start_time', inplace=True)
    print(df_message['Sent Time'])
