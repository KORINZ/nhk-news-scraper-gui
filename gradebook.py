import gspread
import pandas as pd

from datetime import datetime, timedelta
from pathlib import Path

LINE_INCOMING_MESSAGE_FILENAME = 'LINE_Messages'
GRADE_BOOK_FILENAME = '日本語ニュース成績表'
SERVICE_ACCOUNT = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")


def get_quiz_start_end_time(days: int, hour: int, minute: int) -> tuple[datetime, datetime]:
    """Get quiz start and end time."""

    # Get quiz start time from log.txt
    with open('log.txt', 'r') as f:
        quiz_start_time = f.readline().strip('\n').split('.')[0]
        quiz_start_time = datetime.strptime(
            quiz_start_time, '%Y-%m-%d %H:%M:%S')

    # Set quiz end time
    quiz_end_time = quiz_start_time + timedelta(days=days)
    quiz_end_time = quiz_end_time.replace(
        hour=hour, minute=minute, second=0, microsecond=0)

    # Get quiz duration
    time_diff = quiz_end_time - quiz_start_time
    days, hours, minutes = time_diff.days, time_diff.seconds // 3600, (
        time_diff.seconds % 3600) // 60

    # Print quiz start and end time and duration
    print(f'開始時間：{quiz_start_time}\n終了時間：{quiz_end_time}')
    print(f'クイズ時間：{days}日{hours}時間{minutes}分')

    return quiz_start_time, quiz_end_time


quiz_start_time, quiz_end_time = get_quiz_start_end_time(
    days=1, hour=21, minute=0)

line_message = SERVICE_ACCOUNT.open(LINE_INCOMING_MESSAGE_FILENAME)
message_sheet = line_message.worksheet('Messages')
message_records = message_sheet.get_all_records()
df_message = pd.DataFrame(message_records)
df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])


grade_book = SERVICE_ACCOUNT.open(GRADE_BOOK_FILENAME)
grade_sheet = grade_book.worksheet('シート1')

if __name__ == "__main__":
    df_message = df_message.query(
        '@quiz_start_time <= `Sent Time` <= @quiz_end_time')
    print(df_message['Sent Time'])
