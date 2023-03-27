import gspread
import datetime

sa = gspread.service_account(filename="savvy-temple-381905-6e78e62d4ee5.json")

line_message = sa.open('LINE_Messages')
message_sheet = line_message.worksheet('Messages')
grade_book = sa.open('日本語ニュース成績表')
grade_sheet = grade_book.worksheet('シート1')

if __name__ == "__main__":
    print(message_sheet.acell('C3').value)
