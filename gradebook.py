import sys
import os
import pandas as pd
import gspread
import re

from datetime import datetime, timedelta
from pathlib import Path
from tabulate import tabulate
from typing import Union

LINE_INCOMING_MESSAGE_FILENAME = 'LINE_Messages'
LOG_LOCATION = 'push_log.txt'
GRADE_BOOK_FILENAME = '日本語ニュース成績表'
SERVICE_ACCOUNT = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")


def print_quiz_times(quiz_start_time: datetime, now: datetime, quiz_end_time: datetime) -> None:
    """Print the quiz start time, current time, quiz end time, and quiz duration"""
    duration = quiz_end_time - quiz_start_time
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    print(f'開始時間：{quiz_start_time}')
    print(f'現在時間：{now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'終了時間：{quiz_end_time}')
    print(f'クイズ時間：{days}日{hours}時間{minutes}分\n')


def get_quiz_answer() -> str:
    with open(LOG_LOCATION, 'r') as f:
        lines = f.readlines()
        answer = lines[2]
        print(f'単語意味クイズ正解：{answer}')
        return answer


def calculate_point(correct: str, given: str) -> int:
    correct = correct.strip().upper()
    given = given.strip().upper()
    if len(correct) != len(given):
        return 0
    return sum(c == g for c, g in zip(correct, given))


def process_data(raw_data: str, correct_answer: str) -> pd.Series:
    try:
        student_id, given_answer = raw_data.split('\n')
    except ValueError:
        return pd.Series(['0', '0', '0'], index=['student_id', 'given_answer', 'points'])
    points = calculate_point(correct_answer, given_answer)
    return pd.Series([student_id, given_answer, points], index=['student_id', 'given_answer', 'points'])


def parse_quiz_end_time(end_time: str) -> datetime:
    """Parse a quiz end time string to a datetime object."""
    return datetime.strptime(end_time, '%Y-%m-%d %H:%M')


def get_quiz_start_time(quiz_end_time: datetime) -> tuple[datetime, datetime]:
    with open(LOG_LOCATION, 'r') as f:
        quiz_start_time = f.readline().strip('\n').split('.')[0]
        quiz_start_time = datetime.strptime(
            quiz_start_time, '%Y-%m-%d %H:%M:%S')

    now = datetime.now()

    return now, quiz_start_time


def update_grade_book(df_result: pd.DataFrame, quiz_end_time: datetime) -> None:
    grade_book = SERVICE_ACCOUNT.open(GRADE_BOOK_FILENAME)
    grade_sheet = grade_book.worksheet('シート1')
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
        try:
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
        except gspread.exceptions.APIError as e:
            print(f'Error: {e}')


def pretty_print_dataframe(df: pd.DataFrame) -> None:
    data = df.reset_index().values.tolist()
    for row in data:
        row[0] += 2  # Add 2 to the 'Index' column
    header = ['Index'] + df.columns.tolist()
    print(tabulate(data, headers=header, tablefmt='grid'))


def main(end_time: str) -> None:
    """Main function to process the data and update the grade book"""

    quiz_end_time = parse_quiz_end_time(end_time)
    now, quiz_start_time = get_quiz_start_time(quiz_end_time)
    print_quiz_times(quiz_start_time, now, quiz_end_time)

    line_message = SERVICE_ACCOUNT.open(LINE_INCOMING_MESSAGE_FILENAME)
    message_sheet = line_message.worksheet('Messages')
    message_records = message_sheet.get_all_records()
    df_message = pd.DataFrame(message_records)
    df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])

    correct_answer = get_quiz_answer()
    df_message = df_message.query(
        '@quiz_start_time <= `Sent Time` <= @quiz_end_time')
    df_processed = df_message['Message'].apply(
        lambda x: process_data(x, correct_answer))

    df_result = pd.concat([df_message['Sent Time'], df_processed], axis=1)
    try:
        df_result = df_result.query(
            'student_id != "0" or given_answer != "0" or points != "0"')
        pretty_print_dataframe(df_result)
    except pd.errors.UndefinedVariableError:
        print("Error: No data found.")
        sys.exit()

    if quiz_end_time > now:
        print("Warning: quiz_end_time has not been reached. Data will not be updated.")
        sys.exit()
    else:
        update_grade_book(df_result, quiz_end_time)


if __name__ == '__main__':
    # Clearing the terminal
    os.system('cls') if sys.platform.startswith(
        'win32') else os.system('clear')

    # Quiz end time in the format 'YYYY-MM-DD HH:mm'
    main(end_time='2023-03-28 12:00')

    # TODO: Set up a cron job to run this script every day at 12:00 AM
    # TODO: Add a function to send a message to the students who have not submitted their answers
    # TODO: Verify the USER ID as well
