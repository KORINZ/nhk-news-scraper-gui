import customtkinter as ctk
import threading
import sys
import os
import subprocess
import json

from main import main, push_quiz, save_quiz_vocab
from tkinter import messagebox
from webbrowser import open_new_tab
from datetime import datetime

VERSION = "v0.0.3b"
button_colors = ['blue', 'green', 'dark-blue']
ctk.set_default_color_theme(button_colors[2])

DEFAULT_NUMBER_OF_QUESTIONS = "4"

PRONOUN_QUIZ_LOCATION = r'txt_files/pronunciation_quiz.txt'
DEF_QUIZ_LOCATION = r'txt_files/definition_quiz.txt'
LOG_LOCATION = r'txt_files/push_log.txt'
NEWS_ARTICLE_LOCATION = r'txt_files/news_article.txt'
PAST_QUIZ_LOCATION = r'txt_files/past_quiz_data.txt'
NHK_ICON_LOCATION = r'./icon/nhk.ico'
SETTINGS_FILE = "settings.json"
GRADE_BOOK_URL = "www.google.com"
PROJECTION_URL = "https://github.com/KORINZ/nhk_news_web_easy_scraper"


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, datetime_label, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.datetime_label = datetime_label
        self.font = ctk.CTkFont(family="Yu Gothic UI", size=16)
        self._segmented_button.configure(font=self.font)
        self.txt_folder_path = "txt_files"

        # *ファイル Tab
        self.add("ファイル表示")
        self.sub_txt_tabs = ctk.CTkTabview(
            master=self.tab("ファイル表示"))
        self.sub_txt_tabs.pack(fill="both", expand=True)
        self.sub_txt_tabs._segmented_button.configure(
            font=self.font)
        self.textboxes = {}

        def create_txt_tab(self, tab_name, txt_file) -> None:
            """Create sub-tabs with textboxes that display the contents of txt files"""
            self.sub_txt_tabs.add(tab_name)
            self.frame = ctk.CTkFrame(
                master=self.sub_txt_tabs.tab(tab_name))

            self.frame.pack(fill="both", expand=True)

            self.textbox = ctk.CTkTextbox(
                master=self.frame, wrap=ctk.WORD, font=self.font)
            self.textbox.pack(fill="both", expand=True)

            if tab_name == "ログファイル" or tab_name == "過去のクイズ":
                with open(txt_file, 'r', encoding='utf-8') as f:
                    self.textbox.insert('insert', f.read())
            # Store the textbox in the dictionary
            self.textboxes[tab_name] = self.textbox

        # add widgets on tabs in nested Tabview
        create_txt_tab(self, "ニュース文章", NEWS_ARTICLE_LOCATION)
        create_txt_tab(self, "単語意味クイズ", DEF_QUIZ_LOCATION)
        create_txt_tab(self, "読み方クイズ", PRONOUN_QUIZ_LOCATION)
        create_txt_tab(self, "ログファイル", LOG_LOCATION)
        create_txt_tab(self, "過去のクイズ", PAST_QUIZ_LOCATION)

        # *設定 Tab
        self.add("設定")
        self.settings = ctk.CTkFrame(master=self.tab("設定"))
        self.settings.pack(fill="both", expand=True)

        # *テーマ OptionMenu
        self.label_theme = ctk.CTkLabel(
            master=self.settings, text="テーマ:", font=self.font)
        self.label_theme.grid(row=0, column=0, padx=(
            20, 0), pady=20, sticky="nw")
        self.optionmenu_var = ctk.StringVar(value=master.theme)
        self.optionmenu_mapping = {
            "Light": "ライト",
            "Dark": "ダーク",
            "System": "システム"
        }
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.settings,
                                                             values=list(
                                                                 self.optionmenu_mapping.values()),
                                                             command=self.change_appearance_mode_event,
                                                             variable=self.optionmenu_var, font=self.font)
        self.appearance_mode_optionemenu.grid(
            row=0, column=0, padx=(70, 0), pady=20, sticky="nw")

        # *テキストファイルフォルダー開く Button
        self.txt_file_folder_button = ctk.CTkButton(
            master=self.settings, text="テキストファイルフォルダーを開く", command=self.open_txt_files_folder, font=self.font)
        self.txt_file_folder_button.grid(
            row=0, column=0, padx=(0, 20), pady=20, sticky="ne")

        # *成績チェックURL入力 Button
        self.grade_check_url_button = ctk.CTkButton(master=self.settings,
                                                    text="成績チェックURL入力", command=self.open_input_dialog_event, font=self.font)
        self.grade_check_url_button.grid(row=1, column=0, padx=(0, 20),
                                         pady=0, sticky="ne")

        # *LINE機密情報入力 Button
        self.line_info_button = ctk.CTkButton(master=self.settings,
                                              text="LINE機密情報入力", command=self.open_input_dialog_event, font=self.font)
        self.line_info_button.grid(row=2, column=0, padx=(0, 20),
                                   pady=20, sticky="ne")

        # *ヘルプ Button
        self.help_button = ctk.CTkButton(master=self.settings,
                                         text="ヘルプ", command=self.open_project_page, font=self.font)
        self.help_button.grid(row=3, column=0, padx=(0, 20),
                              pady=0, sticky="ne")

        # *時間表示 Switch
        self.display_time_switch = ctk.CTkSwitch(
            master=self.settings, text="時間表示", font=self.font, command=self.toggle_datetime_display)
        self.display_time_switch.grid(
            row=1, column=0, padx=(20, 0), pady=0, sticky="nw")

        # *デフォルトクイズタイプ OptionMenu
        self.label_default_quiz_type = ctk.CTkLabel(master=self.settings,
                                                    text="デフォルトクイズタイプ:", font=self.font)
        self.label_default_quiz_type.grid(row=2, column=0, padx=(
            20, 0), pady=20, sticky="nw")
        self.default_quiz_type_dropdown = ctk.CTkOptionMenu(
            master=self.settings, values=["単語意味クイズ", "読み方クイズ"], font=self.font)
        self.default_quiz_type_dropdown.grid(row=2, column=0, padx=(170, 0),
                                             pady=20, sticky="nw")

        # *デフォルト問題数 Entry
        self.label_default_number_of_questions = ctk.CTkLabel(master=self.settings,
                                                              text="デフォルト最大問題数:", font=self.font)
        self.label_default_number_of_questions.grid(
            row=3, column=0, padx=(20, 0), pady=0, sticky="nw")
        self.set_default_number_of_questions_entry = ctk.CTkEntry(
            master=self.settings, font=self.font, width=32)
        self.set_default_number_of_questions_entry.grid(
            row=3, column=0, padx=(170, 0), pady=0, sticky="nw")

        # *常にすぐLINEに送信 Checkbox
        self.checkbox_always_send_to_line = ctk.CTkCheckBox(master=self.settings,
                                                            text="常にすぐLINEに送信をチェック", font=self.font)
        self.checkbox_always_send_to_line.grid(row=4, column=0, padx=(20, 0),
                                               pady=20, sticky="nw")

        # *保存 Button
        self.button_save = ctk.CTkButton(
            master=self.settings, text="保存", font=self.font, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.save_settings)
        self.button_save.grid(row=5, column=0, padx=(
            20, 0), pady=20, sticky="sw")

        # *バージョン Label
        self.label_version = ctk.CTkLabel(
            master=self.settings, text="バージョン: " + VERSION, font=self.font)
        self.label_version.grid(row=5, column=0, padx=(
            0, 20), pady=20, sticky="se")

        # Configure grid system
        self.settings.grid_rowconfigure(4, weight=1)
        self.settings.grid_columnconfigure(0, weight=1)

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        """Change the appearance mode when the OptionMenu value is changed"""
        english_value = {v: k for k, v in self.optionmenu_mapping.items()}[
            new_appearance_mode]
        ctk.set_appearance_mode(english_value)

    def update_optionmenu_var(self, english_value: str) -> None:
        """Update the value of the OptionMenu variable"""
        japanese_value = self.optionmenu_mapping.get(english_value)
        if japanese_value:
            self.optionmenu_var.set(japanese_value)

    def open_txt_files_folder(self) -> None:
        """Open the folder containing the txt files."""
        if not os.path.exists(self.txt_folder_path):
            os.makedirs(self.txt_folder_path)
        subprocess.run(['explorer', os.path.abspath(self.txt_folder_path)])

    def save_settings(self) -> None:
        """Save the current settings to a file."""
        japanese_value = self.optionmenu_var.get()
        english_value = {v: k for k, v in self.optionmenu_mapping.items()}.get(
            japanese_value)

        settings = {
            "theme": english_value,
            "display_time": 1 if self.display_time_switch.get() == 1 else 0,
            "default_question_type": self.default_quiz_type_dropdown.get(),
            "default_number_of_questions": self.set_default_number_of_questions_entry.get(),
            "always_send_to_line": 1 if self.checkbox_always_send_to_line.get() == 1 else 0,
            # Add other settings (pending)
        }

        try:
            with open(SETTINGS_FILE, "w") as file:
                json.dump(settings, file)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_settings(self, settings_file: dict) -> None:
        """Update the UI according to the provided settings."""
        # Update the OptionMenu value
        theme = settings_file.get("theme")
        if theme:
            self.update_optionmenu_var(theme)

        # Update the display_time switch and toggle the datetime label
        display_time = settings_file.get("display_time")
        if display_time == 1:
            self.display_time_switch.select()  # Set the switch to ON state
        else:
            self.display_time_switch.deselect()  # Set the switch to OFF state
            self.toggle_datetime_display()  # Toggle display_time only if it is set to False

        # Update the default_question_type dropdown
        quiz_type = str(settings_file.get("default_question_type"))
        self.default_quiz_type_dropdown.set(quiz_type)

        # Update the default_number_of_questions entry
        number = settings_file.get("default_number_of_questions")
        self.set_default_number_of_questions_entry.insert(0, number)

        # Update the always_send_to_line checkbox
        status = settings_file.get("always_send_to_line")
        if status == 1:
            self.checkbox_always_send_to_line.select()
        else:
            self.checkbox_always_send_to_line.deselect()

    def toggle_datetime_display(self) -> None:
        """Toggle the date and time label visibility."""
        if self.display_time_switch.get() == 0:
            self.datetime_label.grid_remove()
        else:
            self.datetime_label.grid()

    def open_project_page(self) -> None:
        """Open the project page in the default browser."""
        open_new_tab(PROJECTION_URL)

    def open_input_dialog_event(self) -> None:
        line_token = ctk.CTkInputDialog(
            text="アクセストークンを入力してください:", title="アクセストークン")


class App(ctk.CTk):
    def __init__(self) -> None:
        self.theme = self.read_settings()
        ctk.set_appearance_mode(self.theme)

        super().__init__()
        self.geometry("1000x618")
        self.iconbitmap(NHK_ICON_LOCATION)
        self.title(f'NHK NEWS EASY クイズ作成 CTk GUI {VERSION}')
        self.font = ctk.CTkFont(family="Yu Gothic UI", size=16)

        # Create a label to display the date and time
        self.datetime_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.datetime_label.grid(
            row=3, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.update_datetime_label()

        # Create the tab view
        self.tab_view = MyTabView(
            master=self, datetime_label=self.datetime_label, width=860, height=300)
        self.tab_view.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        self.load_saved_settings()

        # Create the test type radio buttons
        # ? self.line_push_var = tk.BooleanVar()

        # Create the progress bar
        self.label_progress = ctk.CTkLabel(
            master=self, text="プログレス:", font=self.font)
        self.label_progress.grid(
            row=0, column=0, padx=(0, 450), pady=10, sticky="ne")

        self.progressbar = ctk.CTkProgressBar(
            master=self, width=250, height=20)
        self.progressbar.grid(row=0, column=0, padx=(
            0, 180), pady=15, sticky="ne")
        self.progressbar.set(0)

        self.reset_button = ctk.CTkButton(
            master=self, text="やり直す", font=self.font, command=self.start_over)
        self.reset_button.grid(
            row=0, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.reset_button.configure(state="disabled")

        self.label_type = ctk.CTkLabel(
            master=self, text="クイズタイプ:", font=self.font)
        self.label_type.grid(row=0, column=0, padx=(
            20, 0), pady=10, sticky="nw")

        self.quiz_type_dropdown = ctk.CTkOptionMenu(
            master=self, values=["単語意味クイズ", "読み方クイズ"], font=self.font)
        self.quiz_type_dropdown.grid(row=0, column=0, padx=(
            120, 10), pady=10, sticky="nw")

        self.label_number = ctk.CTkLabel(
            master=self, text="最大問題数:", font=self.font)
        self.label_number.grid(
            row=1, column=0, padx=(20, 120), sticky="w")
        self.number_entry = ctk.CTkEntry(
            master=self, font=self.font, width=32)
        self.number_entry.grid(row=1, column=0, padx=(120, 0), sticky="nw")
        self.number_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)

        # Create the increment and decrement buttons
        self.increment_button = ctk.CTkButton(
            master=self, text="▲", width=30)
        self.increment_button.grid(
            row=1, column=0, padx=(160, 0), pady=(0, 0), sticky="w")
        self.decrement_button = ctk.CTkButton(
            master=self, text="▼", width=30)
        self.decrement_button.grid(
            row=1, column=0, padx=(200, 0), pady=(0, 0), sticky="w")
        self.increment_button.configure(command=self.increment_questions)
        self.decrement_button.configure(command=self.decrement_questions)

        self.check_box = ctk.CTkCheckBox(
            master=self, text="すぐLINEに発信", font=self.font)
        self.check_box.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # Create the make and send buttons
        self.button_make = ctk.CTkButton(
            master=self, text="クイズ作成", font=self.font)
        self.button_make.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.button_make.configure(command=self.start_quiz_generation_thread)

        self.button_send = ctk.CTkButton(
            master=self, text="LINEに発信", font=self.font)
        self.button_send.grid(row=3, column=0, padx=180, pady=10, sticky="nw")
        self.button_send.configure(command=self.press_push_quiz_button)
        self.button_send.configure(state="disabled")

        self.button_grade = ctk.CTkButton(
            master=self, text="成績チェック", command=self.open_grade_book, font=self.font)
        self.button_grade.grid(row=3, column=0, padx=340, pady=10, sticky="nw")

        self.grid_rowconfigure(4, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

    def open_grade_book(self) -> None:
        """Open the grade book."""
        open_new_tab(GRADE_BOOK_URL)

    def start_quiz_generation_thread(self) -> None:
        """Start a thread to run the quiz generation function in the background."""
        self.quiz_generation_thread = threading.Thread(
            target=self.run_quiz_generation)
        self.quiz_generation_thread.daemon = True  # Set the daemon attribute to True
        self.quiz_generation_thread.start()

    def run_quiz_generation(self) -> None:
        """Run the quiz generation function in the background."""
        try:
            self.progressbar.set(0)
            self.button_send.configure(state="disabled")
            self.reset_button.configure(state="disabled")
            if self.number_entry.get() == "0":
                messagebox.showerror("エラー", "最大問題数を指定してください。")
                sys.exit(1)
            main(self.quiz_type_dropdown.get(), push=bool(self.check_box.get()),
                 questions=int(self.number_entry.get()), progress_callback=self.update_progressbar)

            # Automatically update the Text widget after quiz generation
            self.update_textboxes()
            # Enable the send button
            self.button_send.configure(state="normal")
            self.reset_button.configure(state="normal")

            if self.check_box.get():
                messagebox.showinfo("成功", "クイズがLINEに送信されました！")
        except ValueError:
            messagebox.showerror("エラー", "最大問題数を指定してください。")
        except PermissionError as e:
            messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")
        except ConnectionError as e:
            messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")
        finally:
            self.progressbar.stop()

    def increment_questions(self) -> None:
        """Increase the value of the questions Entry."""
        current_value_str = self.number_entry.get().strip()
        if not current_value_str.isdigit():
            self.number_entry.delete(0, ctk.END)
            self.number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            self.number_entry.delete(0, ctk.END)
            self.number_entry.insert(0, str(current_value + 1))

    def decrement_questions(self) -> None:
        """Decrease the value of the questions Entry."""
        current_value_str = self.number_entry.get().strip()
        if not current_value_str.isdigit():
            self.number_entry.delete(0, ctk.END)
            self.number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            if current_value > 1:
                self.number_entry.delete(0, ctk.END)
                self.number_entry.insert(0, str(current_value - 1))

    def update_progressbar(self, progress: float) -> None:
        """Update the progressbar in the main window."""
        app.progressbar.set(progress)

    def press_push_quiz_button(self) -> None:
        """Send the quiz to LINE."""
        try:
            if self.quiz_type_dropdown.get() == "読み方クイズ":
                push_quiz(PRONOUN_QUIZ_LOCATION)
            else:
                push_quiz(DEF_QUIZ_LOCATION)
            messagebox.showinfo("成功", "クイズを発信しました！")
            with open(LOG_LOCATION, 'a+', encoding='utf-8') as f:
                f.write('PUSHED\n')
                f.seek(0)
                url = f.readlines()[1]
            save_quiz_vocab(url)
            self.update_textboxes()
        except PermissionError as e:
            messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")

    def update_textboxes(self, initial_load: bool = False) -> None:
        """Clear and update the textboxes after quiz generation."""
        file_tab_mapping = {
            "ニュース文章": NEWS_ARTICLE_LOCATION,
            "単語意味クイズ": DEF_QUIZ_LOCATION,
            "読み方クイズ": PRONOUN_QUIZ_LOCATION,
            "過去のクイズ": PAST_QUIZ_LOCATION,
            "ログファイル": LOG_LOCATION,
        }

        for tab_name, file_location in file_tab_mapping.items():
            textbox = self.tab_view.textboxes[tab_name]

            # Clear the textbox if it's not the log file or the past quiz file
            if not initial_load or (tab_name != "ログファイル" and tab_name != "過去のクイズ"):
                textbox.delete("1.0", ctk.END)

            with open(file_location, "r", encoding="utf-8") as file:
                content = file.read()
                textbox.insert(ctk.END, content)

    def start_over(self) -> None:
        """Reset the app to its initial state."""
        self.number_entry.delete(0, ctk.END)
        self.number_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)
        self.quiz_type_dropdown.set("単語意味クイズ")
        self.check_box.configure(state="normal")
        self.button_send.configure(state="disabled")
        self.progressbar.set(0)

        # Clear the textboxes (except the log file)
        for tab_name, textbox in self.tab_view.textboxes.items():
            if tab_name != "ログファイル" and tab_name != "過去のクイズ":
                textbox.delete("1.0", ctk.END)

    def load_saved_settings(self) -> None:
        """Load the saved settings from the file."""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                saved_settings = json.load(file)
                self.tab_view.update_settings(saved_settings)

    def read_settings(self) -> str:
        """Read the settings from a file."""
        try:
            with open(SETTINGS_FILE, "r") as file:
                settings = json.load(file)
                theme = settings.get("theme")
                return theme
        except FileNotFoundError as e:
            print(f"Settings file not found: {e}")
            sys.exit(1)

    def update_datetime_label(self) -> None:
        """Update the date and time label with the current date and time."""
        def weekday_in_jp(weekday: int) -> str:
            japanese_weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            return japanese_weekdays[weekday]

        now = datetime.now()
        current_time = now.strftime(
            f"%Y-%m-%d ({weekday_in_jp(now.weekday())}) %H:%M:%S")
        self.datetime_label.configure(text=current_time)
        self.after(1000, self.update_datetime_label)


if __name__ == "__main__":
    app = App()
    app.mainloop()
