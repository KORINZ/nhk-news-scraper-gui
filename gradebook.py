import sys
import os
import pandas as pd
import gspread
import tkinter as tk
from tkinter import scrolledtext

from datetime import datetime
from pathlib import Path
from tabulate import tabulate

# Constants
LINE_INCOMING_MESSAGE_FILENAME = 'LINE_Messages'
LOG_LOCATION = 'push_log.txt'
GRADE_BOOK_FILENAME = '日本語ニュース成績表'
SERVICE_ACCOUNT = gspread.service_account(
    filename=Path() / "savvy-temple-381905-6e78e62d4ee5.json")


def format_quiz_times(quiz_start_time: datetime, now: datetime, quiz_end_time: datetime) -> str:
    """Format the quiz start time, current time, quiz end time, and quiz duration"""
    duration = quiz_end_time - quiz_start_time
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    quiz_times_str = (
        f'開始時間：{quiz_start_time}\n'
        f'現在時間：{now.strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'終了時間：{quiz_end_time}\n'
        f'クイズ時間：{days}日{hours}時間{minutes}分\n'
    )

    return quiz_times_str


def get_quiz_answer() -> str:
    """Get the quiz answer from the log file"""
    with open(LOG_LOCATION, 'r') as f:
        lines = f.readlines()
        answer = lines[2]
        return answer.strip()


def calculate_point(correct: str, given: str) -> int:
    """Calculate the number of correct answers"""
    correct = correct.strip().upper()
    given = given.strip().upper()
    if len(correct) != len(given):
        return 0
    return sum(c == g for c, g in zip(correct, given))


def process_data(raw_data: str, correct_answer: str) -> pd.Series:
    """Process the raw data from the LINE message file"""
    try:
        student_id, given_answer = raw_data.split('\n')
    except ValueError:
        return pd.Series(['0', '0', '0'], index=['student_id', 'given_answer', 'points'])
    points = calculate_point(correct_answer, given_answer)
    return pd.Series([student_id, given_answer, points], index=['student_id', 'given_answer', 'points'])


def parse_quiz_end_time(end_time: str) -> datetime:
    """Parse a quiz end time string to a datetime object."""
    return datetime.strptime(end_time, '%Y-%m-%d %H:%M')


def get_quiz_start_time() -> tuple[datetime, datetime]:
    """Get the quiz start time from the log file"""
    with open(LOG_LOCATION, 'r') as f:
        quiz_start_time = f.readline().strip('\n').split('.')[0]
        quiz_start_time = datetime.strptime(
            quiz_start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    return now, quiz_start_time


def update_grade_book(df_result: pd.DataFrame, quiz_end_time: datetime) -> None:
    """Update the grade book with the quiz results"""
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
    """Print a dataframe in a pretty format"""
    data = df.reset_index().values.tolist()
    for row in data:
        row[0] += 2  # Add 2 to the 'Index' column
    header = ['Index'] + df.columns.tolist()
    print(tabulate(data, headers=header, tablefmt='grid'))


def display_table_in_popup(df, quiz_info) -> None:
    """Display the quiz results in a popup window"""
    def tabulate_dataframe(df) -> str:
        """Format a dataframe as a table"""
        header = ['Index'] + df.columns.tolist()
        data = df.reset_index().values.tolist()
        for row in data:
            row[0] += 2
        formatted_table = tabulate(data, headers=header, tablefmt='grid')
        return formatted_table

    table_str = quiz_info + '\n' + tabulate_dataframe(df)
    root = tk.Tk()
    root.title("Quiz Results")
    root.geometry("800x494")  # Set the size of the root window

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")  # Place the frame using grid

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    # Place the text area using grid
    text_area.grid(row=0, column=0, sticky="nsew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    text_area.insert(tk.INSERT, table_str)

    root.mainloop()


def main(end_time: str) -> None:
    """Main function to process the data and update the grade book"""

    # Parse the quiz end time
    quiz_end_time = parse_quiz_end_time(end_time)
    now, quiz_start_time = get_quiz_start_time()
    quiz_times_str = format_quiz_times(quiz_start_time, now, quiz_end_time)
    print(quiz_times_str)

    correct_answer = get_quiz_answer()
    print(f'単語意味クイズ正解：{correct_answer}\n')

    # Get the quiz answers from student messages
    line_message = SERVICE_ACCOUNT.open(LINE_INCOMING_MESSAGE_FILENAME)
    message_sheet = line_message.worksheet('Messages')
    message_records = message_sheet.get_all_records()
    df_message = pd.DataFrame(message_records)
    df_message['Sent Time'] = pd.to_datetime(df_message['Sent Time'])

    # Process the data
    correct_answer = get_quiz_answer()
    df_message = df_message.query(
        '@quiz_start_time <= `Sent Time` <= @quiz_end_time')
    df_processed = df_message['Message'].apply(
        lambda x: process_data(x, correct_answer))

    # Concatenate the processed data with the original data
    df_result = pd.concat([df_message['Sent Time'], df_processed], axis=1)
    try:
        df_result = df_result.query(
            'student_id != "0" or given_answer != "0" or points != "0"')
        pretty_print_dataframe(df_result)

        quiz_info = format_quiz_times(quiz_start_time, now, quiz_end_time)
        correct_answer = get_quiz_answer()
        quiz_info += f'単語意味クイズ正解：{correct_answer}\n'
        display_table_in_popup(df_result, quiz_info)

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
    main(end_time='2023-03-30 22:00')

    # TODO: Set up a cron job to run this script every day at 12:00 AM
    # TODO: Add a function to send a message to the students who have not submitted their answers
    # TODO: Verify the USER ID as well
