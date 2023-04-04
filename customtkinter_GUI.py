import customtkinter as ctk
import threading
import sys
import os
import subprocess
import json

from main import main, push_quiz, save_quiz_vocab
from webbrowser import open_new_tab
from datetime import datetime
from typing import Tuple, Optional


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
    def __init__(self, master, datetime_label, quiz_type_dropdown, quiz_number_entry, instant_push_check_box, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.datetime_label = datetime_label
        self.quiz_type_dropdown = quiz_type_dropdown
        self.quiz_number_entry = quiz_number_entry
        self.instant_push_check_box = instant_push_check_box
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

        # *スケーリング OptionMenu
        self.scaling_label = ctk.CTkLabel(
            self.settings, text="スケーリング:", font=self.font)
        self.scaling_label.grid(
            row=0, column=0, padx=(0, 145), pady=20, sticky="n")
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.settings, values=["80%", "90%", "100%", "110%", "120%"],
                                                     command=self.change_scaling_event, font=self.font)
        self.scaling_optionemenu.grid(
            row=0, column=0, padx=(100, 0), pady=20, sticky="n")

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
            "scaling": self.scaling_optionemenu.get(),
            # Add other settings (pending)
        }

        try:
            with open(SETTINGS_FILE, "w") as file:
                json.dump(settings, file)
            self.show_saved_label()  # Call this function when saving is successful
        except FileNotFoundError as e:
            print(f"Error: {e}")

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
        self.quiz_type_dropdown.set(quiz_type)

        # Update the default_number_of_questions entry
        number = settings_file.get("default_number_of_questions")
        self.set_default_number_of_questions_entry.delete(0, "end")
        self.set_default_number_of_questions_entry.insert(0, number)
        self.quiz_number_entry.insert(0, number)

        # Update the always_send_to_line checkbox
        status = settings_file.get("always_send_to_line")
        if status == 1:
            self.checkbox_always_send_to_line.select()
            self.instant_push_check_box.select()
        else:
            self.checkbox_always_send_to_line.deselect()
            self.instant_push_check_box.deselect()

        # Update the scaling optionmenu
        scaling = str(settings_file.get("scaling"))
        self.scaling_optionemenu.set(scaling)

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

    def change_scaling_event(self, new_scaling: str) -> None:
        """Change the scaling when the OptionMenu value is changed"""
        new_scaling_float = int(new_scaling.strip("%")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def show_saved_label(self) -> None:
        """Display a 'Saved!' label for 2.5 seconds."""
        saved_label = ctk.CTkLabel(
            self.settings, text="保存しました！再起動後に反映されます。", font=self.font)
        saved_label.grid(row=5, column=0, padx=(
            170, 0), pady=20, sticky="sw")
        self.settings.after(2500,
                            self.remove_saved_label, saved_label)

    def remove_saved_label(self, saved_label: ctk.CTkLabel) -> None:
        """Remove the 'Saved!' label from the grid."""
        saved_label.grid_remove()


class App(ctk.CTk):
    def __init__(self) -> None:
        self.theme = self.read_settings()[0]
        self.scaling = int(self.read_settings()[1].strip("%")) / 100
        ctk.set_appearance_mode(self.theme)
        ctk.set_widget_scaling(self.scaling)

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

        # Create the quiz type dropdown
        self.quiz_type_label = ctk.CTkLabel(
            master=self, text="クイズタイプ:", font=self.font)
        self.quiz_type_label.grid(row=0, column=0, padx=(
            20, 0), pady=10, sticky="nw")

        self.quiz_type_dropdown = ctk.CTkOptionMenu(
            master=self, values=["単語意味クイズ", "読み方クイズ"], font=self.font)
        self.quiz_type_dropdown.grid(row=0, column=0, padx=(
            120, 10), pady=10, sticky="nw")

        # Create the number of questions entry
        self.label_number = ctk.CTkLabel(
            master=self, text="最大問題数:", font=self.font)
        self.label_number.grid(
            row=1, column=0, padx=(20, 120), sticky="w")
        self.quiz_number_entry = ctk.CTkEntry(
            master=self, font=self.font, width=32)
        self.quiz_number_entry.grid(
            row=1, column=0, padx=(120, 0), sticky="nw")

        # Create the check box for instant LINE push
        self.instant_push_check_box = ctk.CTkCheckBox(
            master=self, text="すぐLINEに発信", font=self.font)
        self.instant_push_check_box.grid(
            row=2, column=0, padx=20, pady=10, sticky="w")

        # *Create the tab view instance
        self.tab_view = MyTabView(
            master=self, datetime_label=self.datetime_label, quiz_type_dropdown=self.quiz_type_dropdown,
            quiz_number_entry=self.quiz_number_entry, instant_push_check_box=self.instant_push_check_box,
            width=860, height=300)
        self.tab_view.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        self.load_saved_settings()

        # Create feedback message label
        self.feedback_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.feedback_label.grid(
            row=1, column=0, padx=(0, 20), pady=0, sticky="ne")

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

        # Create progress text label
        self.progress_text_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.progress_text_label.grid(
            row=1, column=0, padx=(570, 0), pady=0, sticky="nw")

        # Create the reset button
        self.reset_button = ctk.CTkButton(
            master=self, text="やり直す", font=self.font, command=self.start_over)
        self.reset_button.grid(
            row=0, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.reset_button.configure(state="disabled")

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

        # Create the make and send buttons
        self.generate_quiz_button = ctk.CTkButton(
            master=self, text="クイズ作成", font=self.font)
        self.generate_quiz_button.grid(
            row=3, column=0, padx=20, pady=10, sticky="w")
        self.generate_quiz_button.configure(
            command=self.start_quiz_generation_thread)

        self.send_quiz_button = ctk.CTkButton(
            master=self, text="LINEに発信", font=self.font)
        self.send_quiz_button.grid(
            row=3, column=0, padx=180, pady=10, sticky="nw")
        self.send_quiz_button.configure(command=self.press_push_quiz_button)
        self.send_quiz_button.configure(state="disabled")

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
            # Initialize the quiz generation process
            self.current_index = 0
            self.total_ids = 0
            self.progressbar.set(0)
            self.send_quiz_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")
            self.progress_text_label.configure(text="")
            self.instant_push_check_box.configure(state="disabled")
            self.quiz_number_entry.configure(state="disabled")
            self.increment_button.configure(state="disabled")
            self.decrement_button.configure(state="disabled")
            self.generate_quiz_button.configure(state="disabled")
            self.feedback_label.configure(text="")
            if self.quiz_number_entry.get() <= "0":
                self.show_feedback_label("最大問題数を指定してください。")
                sys.exit(1)

            if self.instant_push_check_box.get() == 1:
                self.quiz_type_dropdown.configure(state="disabled")

            self.progress_text_label.configure(
                text="初期化中")
            self.blink_progress_text_label()

            # *Run the main function from the main module
            main(self.quiz_type_dropdown.get(), push=bool(self.instant_push_check_box.get()),
                 questions=int(self.quiz_number_entry.get()), progress_callback=self.update_progressbar)

            # Update the progress bar and text label
            if not bool(self.instant_push_check_box.get()):
                self.show_feedback_label("作成完了！")
                self.send_quiz_button.configure(state="normal")
            else:
                self.show_feedback_label("作成完了！LINEに送信済み！")
                self.send_quiz_button.configure(state="disabled")

            # Automatically update the text widget after quiz generation
            self.update_textboxes()

            # Enable buttons
            self.reset_button.configure(state="normal")
            self.quiz_type_dropdown.configure(state="normal")
            self.instant_push_check_box.configure(state="normal")
            self.quiz_number_entry.configure(state="normal")
            self.increment_button.configure(state="normal")
            self.decrement_button.configure(state="normal")
            self.generate_quiz_button.configure(state="normal")

        # Handle errors
        except ValueError:
            self.error_handler("最大問題数を指定してください。")
        except PermissionError:
            self.error_handler("LINEのTOKENを確認してください。")
        except ConnectionError:
            self.error_handler("インターネット接続を確認してください。")
        finally:
            self.progressbar.stop()
            self.progress_text_label.configure(text="")

    def increment_questions(self) -> None:
        """Increase the value of the questions Entry."""
        current_value_str = self.quiz_number_entry.get().strip()
        if not current_value_str.isdigit():
            self.quiz_number_entry.delete(0, ctk.END)
            self.quiz_number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            self.quiz_number_entry.delete(0, ctk.END)
            self.quiz_number_entry.insert(0, str(current_value + 1))

    def decrement_questions(self) -> None:
        """Decrease the value of the questions Entry."""
        current_value_str = self.quiz_number_entry.get().strip()
        if not current_value_str.isdigit():
            self.quiz_number_entry.delete(0, ctk.END)
            self.quiz_number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            if current_value > 1:
                self.quiz_number_entry.delete(0, ctk.END)
                self.quiz_number_entry.insert(0, str(current_value - 1))

    def update_progressbar(self, progress: float, index: int, total_ids: int) -> None:
        """Update the progressbar in the main window."""
        self.progressbar.set(progress)
        self.current_index = index
        self.total_ids = total_ids
        self.blink_progress_text_label()

    def press_push_quiz_button(self) -> None:
        """Send the quiz to LINE."""
        try:
            if self.quiz_type_dropdown.get() == "読み方クイズ":
                push_quiz(PRONOUN_QUIZ_LOCATION)
            else:
                push_quiz(DEF_QUIZ_LOCATION)
            self.feedback_label.configure(text="LINEに送信しました！")
            with open(LOG_LOCATION, 'a+', encoding='utf-8') as f:
                f.write('PUSHED\n')
                f.seek(0)
                url = f.readlines()[1]
            save_quiz_vocab(url)
            self.update_textboxes()
        except PermissionError:
            self.error_handler("LINEのTOKENを確認してください。")

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
        self.quiz_number_entry.delete(0, ctk.END)
        self.generate_quiz_button.configure(state="normal")
        self.send_quiz_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        self.progressbar.set(0)
        self.progress_text_label.configure(text="")
        self.feedback_label.configure(text="")
        self.load_saved_settings()

        # Clear the textboxes (except the log and past_quiz files)
        for tab_name, textbox in self.tab_view.textboxes.items():
            if tab_name != "ログファイル" and tab_name != "過去のクイズ":
                textbox.delete("1.0", ctk.END)

    def load_saved_settings(self) -> None:
        """Load the saved settings from the file."""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                saved_settings = json.load(file)
                self.tab_view.update_settings(saved_settings)

    def read_settings(self) -> Tuple[str, ...]:
        """Read the settings from a file."""
        try:
            with open(SETTINGS_FILE, "r") as file:
                settings = json.load(file)
                theme = settings.get("theme")
                scaling = settings.get("scaling")
                return theme, scaling
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

    def show_feedback_label(self, text) -> None:
        """Show the success label."""
        self.feedback_label.configure(text=text)

    def blink_progress_text_label(self) -> None:
        """Blink the progress text label."""
        if self.current_index == 0 and self.feedback_label:
            current_text = self.progress_text_label.cget("text")
            if current_text == "初期化中":
                new_text = "初期化中・"
            elif current_text == "初期化中・":
                new_text = "初期化中・・"
            elif current_text == "初期化中・・":
                new_text = "初期化中・・・"
            else:
                new_text = "初期化中"

            self.progress_text_label.configure(text=new_text)
            self.after(300, self.blink_progress_text_label)
        elif self.generate_quiz_button.cget("state") == "disabled":
            base_text = f"クイズを作成中({self.current_index}/{self.total_ids})"
            # Get the dot_counter or set it to 0 if not exists
            dot_counter = getattr(self, "dot_counter", 0)

            dots = "・" * dot_counter  # Generate dots based on the dot_counter value
            new_text = base_text + dots
            self.progress_text_label.configure(text=new_text)

            # Cycle through 0, 1, 2, 3 for the dot_counter
            dot_counter = (dot_counter + 1) % 4
            self.dot_counter = dot_counter
            self.after(2000, self.blink_progress_text_label)
        else:
            self.progress_text_label.configure(text="")

    def error_handler(self, error_text: str) -> None:
        """Handle errors."""
        self.progress_text_label.configure(text="")
        self.feedback_label.configure(text=f"エラー：{error_text}")
        self.reset_button.configure(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()
