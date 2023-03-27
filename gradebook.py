import gspread
import pandas as pd

from datetime import datetime
from pathlib import Path

now = datetime.now()

sa = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")


with open('log.txt', 'r') as f:
    quiz_start_time = f.readline().strip('\n')
    quiz_start_time = datetime.strptime(
        quiz_start_time, '%Y-%m-%d %H:%M:%S.%f')
    print(quiz_start_time)

line_message = sa.open('LINE_Messages')
message_sheet = line_message.worksheet('Messages')
message_records = message_sheet.get_all_records()
df_message = pd.DataFrame(message_records)
df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])


grade_book = sa.open('日本語ニュース成績表')
grade_sheet = grade_book.worksheet('シート1')

if __name__ == "__main__":
    print(df_message['Sent Time'])
