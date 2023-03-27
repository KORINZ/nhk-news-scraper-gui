import sys
import pandas as pd
import gspread
from datetime import datetime, timedelta, date
from pathlib import Path

LINE_INCOMING_MESSAGE_FILENAME = 'LINE_Messages'
GRADE_BOOK_FILENAME = '日本語ニュース成績表'
SERVICE_ACCOUNT = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")


def get_quiz_answer() -> str:
    with open('log.txt', 'r') as f:
        lines = f.readlines()
        return lines[2]


def calculate_point(correct: str, given: str) -> int:
    return sum(c == g for c, g in zip(correct, given))


def process_data(raw_data, correct_answer):
    student_id, given_answer = raw_data.split('\n')
    points = calculate_point(correct_answer, given_answer)
    return pd.Series([student_id, given_answer, points], index=['student_id', 'given_answer', 'points'])


def get_quiz_start_end_time(days: int, hour: int, minute: int) -> tuple[datetime, datetime]:
    with open('log.txt', 'r') as f:
        quiz_start_time = f.readline().strip('\n').split('.')[0]
        quiz_start_time = datetime.strptime(
            quiz_start_time, '%Y-%m-%d %H:%M:%S')

    quiz_end_time = quiz_start_time + timedelta(days=days)
    quiz_end_time = quiz_end_time.replace(
        hour=hour, minute=minute, second=0, microsecond=0)

    time_diff = quiz_end_time - quiz_start_time
    days, hours, minutes = time_diff.days, time_diff.seconds // 3600, (
        time_diff.seconds % 3600) // 60

    print(f'開始時間：{quiz_start_time}\n終了時間：{quiz_end_time}')
    print(f'クイズ時間：{days}日{hours}時間{minutes}分')

    return quiz_start_time, quiz_end_time


def main():
    quiz_start_time, quiz_end_time = get_quiz_start_end_time(
        days=1, hour=21, minute=0)

    line_message = SERVICE_ACCOUNT.open(LINE_INCOMING_MESSAGE_FILENAME)
    message_sheet = line_message.worksheet('Messages')
    message_records = message_sheet.get_all_records()
    df_message = pd.DataFrame(message_records)
    df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])

    grade_book = SERVICE_ACCOUNT.open(GRADE_BOOK_FILENAME)
    grade_sheet = grade_book.worksheet('シート1')

    correct_answer = get_quiz_answer()
    df_message = df_message.query(
        '@quiz_start_time <= `Sent Time` <= @quiz_end_time')
    df_message = df_message['Message'].apply(
        lambda x: process_data(x, correct_answer))
    print(df_message)

    now = datetime.now()

    if quiz_end_time > now:
        print("Error: quiz_end_time has not been reached.")
        sys.exit()
    else:
        quiz_end_time_str = quiz_end_time.date().strftime('%Y/%m/%d')

    header_row = grade_sheet.row_values(1)
    if quiz_end_time_str not in header_row:
        col_num = len(header_row) + 1
        grade_sheet.update_cell(1, col_num, quiz_end_time_str)
        header_row.append(quiz_end_time_str)

    # Find the index of the date column
    date_col_idx = header_row.index(quiz_end_time_str) + 1

    for _, row in df_message.iterrows():
        student_id = row['student_id']
        points = row['points']

        # Try to find the student ID in the sheet
        student_id_cell = grade_sheet.find(student_id)

        if student_id_cell:
            # If the student ID exists, update the points in the date column only if the cell is empty
            existing_points = grade_sheet.cell(
                student_id_cell.row, date_col_idx).value
            if not existing_points:  # If the cell is empty
                grade_sheet.update_cell(
                    student_id_cell.row, date_col_idx, points)
        else:
            # If the student ID doesn't exist, append a new row with the student ID and points
            new_row = [student_id] + [''] * (date_col_idx - 2) + [points]
            grade_sheet.append_row(new_row)


if __name__ == '__main__':
    main()
