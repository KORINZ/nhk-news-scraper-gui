import sys
import pandas as pd
import gspread
from datetime import datetime, timedelta
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
    if len(correct) != len(given):
        return 0
    return sum(c == g for c, g in zip(correct, given.upper()))


def process_data(raw_data: str, correct_answer: str) -> pd.Series:
    try:
        student_id, given_answer = raw_data.split('\n')
    except ValueError:
        return pd.Series(['0', '0', '0'], index=['student_id', 'given_answer', 'points'])
    points = calculate_point(correct_answer, given_answer)
    return pd.Series([student_id, given_answer, points], index=['student_id', 'given_answer', 'points'])


def get_quiz_start_end_time(days: int, hour: int, minute: int) -> tuple[datetime, datetime, datetime]:
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

    if days < 0 or hours < 0 or minutes < 0:
        print("Error: quiz_end_time is earlier than quiz_start_time.")
        sys.exit()

    now = datetime.now()
    print(f'開始時間：{quiz_start_time}')
    print(f'現在時間：{now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'終了時間：{quiz_end_time}')
    print(f'クイズ時間：{days}日{hours}時間{minutes}分')

    return now, quiz_start_time, quiz_end_time


def main() -> None:
    now, quiz_start_time, quiz_end_time = get_quiz_start_end_time(
        days=0, hour=17, minute=1)

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
    df_processed = df_message['Message'].apply(
        lambda x: process_data(x, correct_answer))

    df_result = pd.concat([df_message['Sent Time'], df_processed], axis=1)
    try:
        df_result = df_result.query(
            'student_id != "0" or given_answer != "0" or points != "0"')
        print(df_result)
    except pd.errors.UndefinedVariableError:
        print("Error: No data found.")
        sys.exit()

    if quiz_end_time > now:
        print("Warning: quiz_end_time has not been reached. Data will not be updated.")
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

    for _, row in df_result.iterrows():
        sent_time = row['Sent Time']
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
