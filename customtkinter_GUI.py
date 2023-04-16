# Standard library imports
import sys
import os
import subprocess
import json
from datetime import datetime
from typing import Tuple, Callable
from webbrowser import open_new_tab
from tkinter import TclError

# Third-party imports
import customtkinter as ctk
import threading
from requests.exceptions import ConnectionError


# TODO: Add icon for MacOS
# TODO: Fix import error when using sentiment analysis


# Local imports
from main import main, push_quiz, save_quiz_vocab

# Version number
VERSION = "v2.2.0"

# File locations
PRONOUN_QUIZ_LOCATION = r"./txt_files/pronunciation_quiz.txt"
DEF_QUIZ_LOCATION = r"./txt_files/definition_quiz.txt"
LOG_LOCATION = r"./txt_files/push_log.txt"
NEWS_ARTICLE_LOCATION = r"./txt_files/news_article.txt"
PAST_QUIZ_LOCATION = r"./txt_files/past_quiz_data.txt"
NHK_ICON_LOCATION = r"./icons/nhk.ico"
LINE_ICON_LOCATION = r"./icons/LINE.ico"
ALERT_ICON_LOCATION = r"./icons/alert.ico"
SHEET_ICON_LOCATION = r"./icons/sheet.ico"
TOKEN_ID_LOCATION = r"./json_files/secrets.json"
SETTINGS_FILE_LOCATION = r"./json_files/settings.json"
JSON_FOLDER_PATH = r"./json_files"
TXT_FOLDER_PATH = r"./txt_files"


def create_default_settings_file() -> None:
    """Create a default settings file if it doesn't exist."""
    default_settings = {
        "theme": "Dark",
        "button_color": "dark-blue",
        "display_time": 1,
        "default_question_type": "単語意味クイズ",
        "default_number_of_questions": "5",
        "always_send_to_line": 0,
        "send_to_all": 0,
        "scaling": "110%",
        "maximize_screen_check_box": 0,
        "emotion_analysis_switch": 0,
        "grade_book_url": "https://www.google.com",
    }
    if not os.path.exists(JSON_FOLDER_PATH):
        os.makedirs(JSON_FOLDER_PATH)
    with open(SETTINGS_FILE_LOCATION, "w", encoding="utf-8") as settings_file:
        json.dump(default_settings, settings_file,
                  indent=4, ensure_ascii=False)


def load_grade_book_url() -> str:
    """Load the grade book URL from the JSON file."""
    if not os.path.exists(SETTINGS_FILE_LOCATION):
        create_default_settings_file()

    with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as settings_file:
        data = json.load(settings_file)

    return data.get("grade_book_url", "")


# Load the URLs from the JSON file
GRADE_BOOK_URL = load_grade_book_url()
PROJECTION_URL = "https://github.com/KORINZ/nhk_news_web_easy_scraper"


class SubTab:
    """Custom sub-tab class that contains a textbox."""

    def __init__(self, parent, tab_name, txt_file) -> None:
        self.textbox = None
        self.frame = None
        self.parent = parent
        self.tab_name = tab_name
        self.txt_file = txt_file
        self.create_tab()

    def create_tab(self) -> None:
        """Create a sub-tab and a textbox in it."""
        self.parent.sub_txt_tabs.add(self.tab_name)
        self.frame = ctk.CTkFrame(
            master=self.parent.sub_txt_tabs.tab(self.tab_name))
        self.frame.pack(fill="both", expand=True)

        self.textbox = ctk.CTkTextbox(
            master=self.frame, wrap=ctk.WORD, font=self.parent.font
        )
        self.textbox.pack(fill="both", expand=True)

        directory = os.path.dirname(self.txt_file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.isfile(self.txt_file):
            with open(self.txt_file, "w", encoding="utf-8"):
                pass

        if self.tab_name == "ログファイル" or self.tab_name == "過去のクイズ":
            with open(self.txt_file, "r", encoding="utf-8") as f:
                self.textbox.insert("insert", f.read())

        self.parent.textboxes[self.tab_name] = self.textbox


class MainTab(ctk.CTkTabview):
    """Custom Tabview class that contains article and settings tab."""

    def __init__(
        self,
        master,
        datetime_label,
        quiz_type_dropdown,
        quiz_number_entry,
        instant_push_check_box,
        broadcast_on_label,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.confirm_delete_past_quizzes_button = None
        self.cancel_delete_past_quizzes_button = None
        self.datetime_label = datetime_label
        self.quiz_type_dropdown = quiz_type_dropdown
        self.quiz_number_entry = quiz_number_entry
        self.instant_push_check_box = instant_push_check_box
        self.broadcast_on_label = broadcast_on_label
        self.font = ctk.CTkFont(family="Yu Gothic UI", size=15)
        self._segmented_button.configure(font=self.font)
        self.txt_folder_path = TXT_FOLDER_PATH
        self.json_folder_path = JSON_FOLDER_PATH

        # *ファイル Tab
        self.add("ファイル表示")
        self.sub_txt_tabs = ctk.CTkTabview(master=self.tab("ファイル表示"))
        self.sub_txt_tabs.pack(fill="both", expand=True)
        self.sub_txt_tabs._segmented_button.configure(font=self.font)
        self.textboxes = {}

        # add widgets on tabs in nested Tabview
        SubTab(self, "ニュース文章", NEWS_ARTICLE_LOCATION)
        SubTab(self, "単語意味クイズ", DEF_QUIZ_LOCATION)
        SubTab(self, "読み方クイズ", PRONOUN_QUIZ_LOCATION)
        SubTab(self, "過去のクイズ", PAST_QUIZ_LOCATION)
        SubTab(self, "ログファイル", LOG_LOCATION)

        # Switch to the "ログファイル" tab by default
        self.sub_txt_tabs.set("ログファイル")

        # *設定 Tab
        self.add("設定")
        self.set("設定")
        self.settings = ctk.CTkFrame(master=self.tab("設定"))
        self.settings.pack(fill="both", expand=True)

        # *テーマ OptionMenu
        self.label_theme = ctk.CTkLabel(
            master=self.settings, text="テーマ:", font=self.font
        )
        self.label_theme.grid(row=0, column=0, padx=(
            20, 0), pady=20, sticky="nw")
        self.theme_optionmenu_var = ctk.StringVar(value=master.theme)
        self.theme_optionmenu_mapping = {
            "Light": "ライト",
            "Dark": "ダーク",
            "System": "システム",
        }
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.settings,
            values=list(self.theme_optionmenu_mapping.values()),
            command=self.change_appearance_mode_event_theme,
            variable=self.theme_optionmenu_var,
            font=self.font,
            width=100,
        )
        self.appearance_mode_optionemenu.grid(
            row=0, column=0, padx=(80, 0), pady=20, sticky="nw"
        )

        # *ボタン色 OptionMenu
        self.label_button_color = ctk.CTkLabel(
            master=self.settings, text="ボタン色(再起動する):", font=self.font
        )
        self.label_button_color.grid(
            row=1, column=0, padx=(20, 0), pady=0, sticky="nw")
        self.button_color_optionmenu_var = ctk.StringVar(
            value=master.button_color)
        self.button_color_optionmenu_mapping = {
            "blue": "ブルー",
            "dark-blue": "瑠璃色",
            "green": "若竹色",
        }
        self.button_color_optionmenu = ctk.CTkOptionMenu(
            self.settings,
            values=list(self.button_color_optionmenu_mapping.values()),
            variable=self.button_color_optionmenu_var,
            font=self.font,
            command=lambda _: self.change_appearance_mode_event_button_color(
                self.button_color_optionmenu_var.get()
            ),
            width=100,
        )

        self.button_color_optionmenu.grid(
            row=1, column=0, padx=(180, 0), pady=0, sticky="nw"
        )

        # *時間表示 Switch
        self.display_datetime_switch = ctk.CTkSwitch(
            master=self.settings,
            text="時間表示",
            font=self.font,
            command=self.toggle_datetime_display,
        )
        self.display_datetime_switch.grid(
            row=2, column=0, padx=(20, 0), pady=20, sticky="nw"
        )

        # *デフォルトクイズタイプ OptionMenu
        self.label_default_quiz_type = ctk.CTkLabel(
            master=self.settings, text="デフォルトクイズタイプ:", font=self.font
        )
        self.label_default_quiz_type.grid(
            row=3, column=0, padx=(20, 0), pady=0, sticky="nw"
        )
        self.default_quiz_type_dropdown = ctk.CTkOptionMenu(
            master=self.settings, values=["単語意味クイズ", "読み方クイズ"], font=self.font
        )
        self.default_quiz_type_dropdown.grid(
            row=3, column=0, padx=(180, 0), pady=0, sticky="nw"
        )

        # *デフォルト問題数 Entry
        self.label_default_number_of_questions = ctk.CTkLabel(
            master=self.settings, text="デフォルト最大問題数:", font=self.font
        )
        self.label_default_number_of_questions.grid(
            row=4, column=0, padx=(20, 0), pady=20, sticky="nw"
        )
        self.set_default_number_of_questions_entry = ctk.CTkEntry(
            master=self.settings, font=self.font, width=32
        )
        self.set_default_number_of_questions_entry.grid(
            row=4, column=0, padx=(180, 0), pady=20, sticky="nw"
        )

        # *常にすぐLINEに送信 Checkbox
        self.checkbox_always_send_to_line = ctk.CTkCheckBox(
            master=self.settings, text="常にすぐLINEに送信をチェック", font=self.font
        )
        self.checkbox_always_send_to_line.grid(
            row=5, column=0, padx=(20, 0), pady=0, sticky="nw"
        )

        # *スケーリング OptionMenu
        self.scaling_label = ctk.CTkLabel(
            self.settings, text="スケーリング:", font=self.font)
        self.scaling_label.grid(
            row=0, column=0, padx=(0, 125), pady=20, sticky="n")
        self.scaling_optionemenu = ctk.CTkOptionMenu(
            self.settings,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event,
            font=self.font,
            width=100,
        )
        self.scaling_optionemenu.grid(
            row=0, column=0, padx=(90, 0), pady=20, sticky="n"
        )

        # *起動時ウィンドウ最大化 Checkbox
        self.maximize_screen_check_box = ctk.CTkCheckBox(
            master=self.settings,
            text="起動時ウィンドウ最大化",
            font=self.font,
        )
        self.maximize_screen_check_box.grid(
            row=1, column=0, padx=(0, 0), pady=0, sticky="n"
        )

        # *成績表URL入力 Button
        self.grade_check_url_button = ctk.CTkButton(
            master=self.settings,
            text="成績表URL入力",
            command=self.enter_grade_book_url,
            font=self.font,
        )
        self.grade_check_url_button.grid(
            row=2, column=0, padx=(0, 0), pady=20, sticky="n"
        )

        # *LINE機密情報入力 Button
        self.line_info_button = ctk.CTkButton(
            master=self.settings,
            text="LINE機密情報入力",
            command=self.enter_line_confidential,
            font=self.font,
        )
        self.line_info_button.grid(
            row=3, column=0, padx=(0, 0), pady=0, sticky="n")

        # *全員に発信 Switch
        self.broadcast_switch = ctk.CTkSwitch(
            master=self.settings,
            text="全員に発信",
            font=self.font,
            command=self.toggle_send_to_all_label,
        )
        self.broadcast_switch.grid(
            row=4, column=0, padx=(0, 0), pady=20, sticky="n")

        # *感情分析 Switch
        self.emotion_analysis_switch = ctk.CTkSwitch(
            master=self.settings,
            text="ログファイルの感情分析",
            font=self.font,
        )
        self.emotion_analysis_switch.grid(
            row=5, column=0, padx=(0, 0), pady=0, sticky="n"
        )

        # *テキストファイルフォルダー開く Button
        self.txt_file_folder_button = ctk.CTkButton(
            master=self.settings,
            text="テキストファイルフォルダーを開く",
            command=self.open_txt_files_folder,
            font=self.font,
        )
        self.txt_file_folder_button.grid(
            row=0, column=0, padx=(0, 20), pady=20, sticky="ne"
        )

        # *JSONフォルダーを開く Button
        self.open_json_folder = ctk.CTkButton(
            master=self.settings,
            text="JSONフォルダーを開く",
            font=self.font,
            command=self.open_json_files_folder,
        )
        self.open_json_folder.grid(
            row=1, column=0, padx=(0, 20), pady=0, sticky="ne")

        # *過去のクイズを削除 Button
        self.delete_past_quizzes_button = ctk.CTkButton(
            master=self.settings,
            text="過去のクイズを削除",
            command=self.confirm_delete_past_quizzes,
            font=self.font,
            hover_color="#8B0000",
        )
        self.delete_past_quizzes_button.grid(
            row=2, column=0, padx=(0, 20), pady=20, sticky="ne"
        )

        # *削除した Label
        self.past_quizzes_deleted_label = ctk.CTkLabel(
            master=self.settings, text="", font=self.font
        )
        self.past_quizzes_deleted_label.grid(
            row=4, column=0, padx=(0, 20), pady=20, sticky="ne"
        )

        # *ヘルプ Button
        self.help_button = ctk.CTkButton(
            master=self.settings,
            text="ヘルプ",
            command=self.open_project_page,
            font=self.font,
        )
        self.help_button.grid(
            row=3, column=0, padx=(0, 20), pady=0, sticky="ne")

        # *URL・LINE機密情報の保存成功 Label
        self.url_line_confidential_saved_label = ctk.CTkLabel(
            master=self.settings, text="", font=self.font
        )
        self.url_line_confidential_saved_label.grid(
            row=4, column=0, padx=(0, 20), pady=20, sticky="ne"
        )

        # *保存 Button
        self.save_settings_button = ctk.CTkButton(
            master=self.settings,
            text="保存",
            font=self.font,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.save_settings,
        )
        self.save_settings_button.grid(
            row=6, column=0, padx=(20, 0), pady=20, sticky="sw"
        )

        # *バージョン Label
        self.label_version = ctk.CTkLabel(
            master=self.settings,
            text="まりな先生 (2023) NHK NEWS WEB EASY 日本語クイズ作成: " + VERSION,
            font=self.font,
        )
        self.label_version.grid(
            row=6, column=0, padx=(0, 20), pady=20, sticky="se")

        # Configure grid system
        self.settings.grid_rowconfigure(5, weight=1)
        self.settings.grid_columnconfigure(0, weight=1)

    @staticmethod
    def set_icon(window: ctk.CTkToplevel, icon: str) -> None:
        try:
            window.iconbitmap(icon)
        except TclError:
            pass

    def confirm_delete_past_quizzes(self) -> None:
        """Confirm delete past quizzes popup window"""
        delete_past_quiz_popup = ctk.CTkToplevel(self)
        delete_past_quiz_popup.title("過去のクイズを削除")
        # ?Bug from customtkinter
        self.after(
            200, lambda: self.set_icon(
                delete_past_quiz_popup, ALERT_ICON_LOCATION)
        )

        pop_width, pop_height, x_position, y_position = self.calculate_window_size(
            popup_width=600, popup_height=200
        )
        delete_past_quiz_popup.geometry(
            f"{pop_width}x{pop_height}+{x_position}+{y_position}"
        )

        ctk.CTkLabel(
            delete_past_quiz_popup,
            text="過去のクイズを完全に削除しますか？「CONFIRM」を入力してください。",
            font=self.font,
        ).grid(row=0, column=0, padx=(0, 0), pady=20, sticky="n")
        confirm_entry = ctk.CTkEntry(
            delete_past_quiz_popup, width=400, font=self.font)
        confirm_entry.grid(row=1, column=0, padx=(0, 0), pady=0, sticky="n")

        self.cancel_delete_past_quizzes_button = ctk.CTkButton(
            delete_past_quiz_popup,
            text="キャンセル",
            font=self.font,
            command=delete_past_quiz_popup.destroy,
        )
        self.cancel_delete_past_quizzes_button.grid(
            row=2, column=0, padx=(20, 0), pady=20, sticky="w"
        )
        self.confirm_delete_past_quizzes_button = ctk.CTkButton(
            delete_past_quiz_popup,
            text="削除",
            font=self.font,
            command=lambda: self.delete_past_quizzes(delete_past_quiz_popup)
            if confirm_entry.get() == "CONFIRM"
            else None,
        )
        self.confirm_delete_past_quizzes_button.grid(
            row=2, column=0, padx=(0, 20), pady=20, sticky="e"
        )

        # Configure the rows and columns to have weight for scaling
        delete_past_quiz_popup.grid_rowconfigure(0, weight=1)
        delete_past_quiz_popup.grid_rowconfigure(1, weight=1)
        delete_past_quiz_popup.grid_rowconfigure(
            2, weight=1
        )  # Added a row for the buttons
        delete_past_quiz_popup.grid_columnconfigure(0, weight=1)

        delete_past_quiz_popup.grab_set()

    @staticmethod
    def restart_app() -> None:
        """Restart the app"""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def delete_past_quizzes(self, popup) -> None:
        """Delete all the past quizzes in the quizzes folder."""
        with open(PAST_QUIZ_LOCATION, "w", encoding="utf-8") as f:
            f.write("")
            self.past_quizzes_deleted_label.configure(text="過去のクイズを削除しました。")
            self.past_quizzes_deleted_label.after(
                3000, lambda: self.past_quizzes_deleted_label.configure(
                    text="")
            )

        past_quiz = self.textboxes["過去のクイズ"]
        past_quiz.delete(1.0, ctk.END)
        popup.destroy()

    def change_appearance_mode_event_theme(self, new_appearance_mode: str) -> None:
        """Change the appearance mode when the OptionMenu value is changed"""
        english_value = {v: k for k, v in self.theme_optionmenu_mapping.items()}[
            new_appearance_mode
        ]
        ctk.set_appearance_mode(english_value)

    def change_appearance_mode_event_button_color(
        self, new_appearance_mode: str
    ) -> None:
        """Change the appearance mode when the OptionMenu value is changed"""
        english_value = {v: k for k, v in self.button_color_optionmenu_mapping.items()}[
            new_appearance_mode
        ]

        # Read the JSON file
        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Update the value in the dictionary
        settings["button_color"] = english_value

        # Write the updated dictionary back to the JSON file
        with open(SETTINGS_FILE_LOCATION, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

        self.restart_app()

    def update_theme_optionmenu_var(self, english_value: str) -> None:
        """Update the value of the OptionMenu variable"""
        japanese_value = self.theme_optionmenu_mapping.get(english_value)
        if japanese_value:
            self.theme_optionmenu_var.set(japanese_value)

    def update_button_color_optionmenu_var(self, english_value: str) -> None:
        """Update the value of the OptionMenu variable"""
        japanese_value = self.button_color_optionmenu_mapping.get(
            english_value)
        if japanese_value:
            self.button_color_optionmenu_var.set(japanese_value)

    def open_txt_files_folder(self) -> None:
        """Open the folder containing the txt files."""
        if not os.path.exists(self.txt_folder_path):
            os.makedirs(self.txt_folder_path)
        subprocess.run(["explorer", os.path.abspath(self.txt_folder_path)])

    def open_json_files_folder(self) -> None:
        """Open the folder containing the json files."""
        subprocess.run(["explorer", os.path.abspath(self.json_folder_path)])

    def save_settings(self) -> None:
        """Save the current settings to a file without overwriting grade_book_url."""
        theme_japanese_value = self.theme_optionmenu_var.get()
        theme_english_value = {
            v: k for k, v in self.theme_optionmenu_mapping.items()
        }.get(theme_japanese_value)

        button_color_japanese_value = self.button_color_optionmenu_var.get()
        button_color_english_value = {
            v: k for k, v in self.button_color_optionmenu_mapping.items()
        }.get(button_color_japanese_value)

        # Load existing settings
        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as file:
            settings = json.load(file)

        # Update settings with new values
        settings.update(
            {
                "theme": theme_english_value,
                "button_color": button_color_english_value,
                "display_time": 1 if self.display_datetime_switch.get() == 1 else 0,
                "default_question_type": self.default_quiz_type_dropdown.get(),
                "default_number_of_questions": self.set_default_number_of_questions_entry.get(),
                "always_send_to_line": 1
                if self.checkbox_always_send_to_line.get() == 1
                else 0,
                "send_to_all": 1 if self.broadcast_switch.get() == 1 else 0,
                "scaling": self.scaling_optionemenu.get(),
                "maximize_screen_check_box": 1
                if self.maximize_screen_check_box.get() == 1
                else 0,
                "emotion_analysis_switch": 1
                if self.emotion_analysis_switch.get() == 1
                else 0,
            }
        )

        try:
            with open(SETTINGS_FILE_LOCATION, "w", encoding="utf-8") as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)
            self.show_saved_label()  # Call this function when saving is successful
        except FileNotFoundError as e:
            print(f"Error: {e}")

    def update_settings(self, settings_file: dict) -> None:
        """Update the UI according to the provided settings."""
        # Update the OptionMenu value
        theme = settings_file.get("theme")
        if theme:
            self.update_theme_optionmenu_var(theme)

        button_color = settings_file.get("button_color")
        if button_color:
            self.update_button_color_optionmenu_var(button_color)

        # Update the display_time switch and toggle the datetime label
        display_time = settings_file.get("display_time")
        if display_time == 1:
            self.display_datetime_switch.select()  # Set the switch to ON state
            self.toggle_datetime_display()  # Toggle display_time only if it is set to True
        else:
            self.display_datetime_switch.deselect()  # Set the switch to OFF state
            self.toggle_datetime_display()  # Toggle display_time only if it is set to False

        # Update the broadcast switch
        send_to_all = settings_file.get("send_to_all")
        if send_to_all == 1:
            self.broadcast_switch.select()
            self.toggle_send_to_all_label()
        else:
            self.broadcast_switch.deselect()
            self.toggle_send_to_all_label()

        # Update the emotion_analysis_switch
        emotion_analysis = settings_file.get("emotion_analysis_switch")
        if emotion_analysis == 1:
            self.emotion_analysis_switch.select()
        else:
            self.emotion_analysis_switch.deselect()

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
        if settings_file.get("always_send_to_line") == 1:
            self.checkbox_always_send_to_line.select()
            self.instant_push_check_box.select()
        else:
            self.checkbox_always_send_to_line.deselect()
            self.instant_push_check_box.deselect()

        # Update the maximize_screen_check_box
        if settings_file.get("maximize_screen_check_box") == 1:
            self.maximize_screen_check_box.select()
        else:
            self.maximize_screen_check_box.deselect()

        # Update the scaling optionmenu
        scaling = str(settings_file.get("scaling"))
        self.scaling_optionemenu.set(scaling)

    def toggle_send_to_all_label(self) -> None:
        """Display send to all label."""
        if self.broadcast_switch.get() == 0:
            self.broadcast_on_label.grid_remove()
        else:
            self.broadcast_on_label.grid()

    def toggle_datetime_display(self) -> None:
        """Toggle the date and time label visibility."""
        if self.display_datetime_switch.get() == 0:
            self.datetime_label.grid_remove()
        else:
            self.datetime_label.grid()

    @staticmethod
    def open_project_page() -> None:
        """Open the project page in the default browser."""
        open_new_tab(PROJECTION_URL)

    def calculate_window_size(self, popup_width, popup_height) -> Tuple:
        """Calculate the window size based on the screen size."""
        main_window_width = self.master.winfo_width()
        main_window_height = self.master.winfo_height()
        main_window_x = self.master.winfo_x()
        main_window_y = self.master.winfo_y()
        x_position = main_window_x + \
            (main_window_width // 2) - (popup_width // 2)
        y_position = main_window_y + \
            (main_window_height // 2) - (popup_height // 2)
        return popup_width, popup_height, x_position, y_position

    def add_save_cancel_buttons(
        self, popup: ctk.CTkToplevel, row: int, column: int, command: Callable
    ) -> None:
        """Add the save and cancel buttons to the popup."""
        save_button = ctk.CTkButton(
            popup, text="保存", command=command, font=self.font)
        save_button.grid(row=row, column=column,
                         padx=(0, 15), pady=10, sticky="se")

        cancel_button = ctk.CTkButton(
            popup, text="キャンセル", command=popup.destroy, font=self.font
        )
        cancel_button.grid(row=row, column=column,
                           padx=(15, 0), pady=10, sticky="sw")

    def enter_grade_book_url(self) -> None:
        """Enter the grade book URL popup."""
        grade_book_url_popup = ctk.CTkToplevel(self)
        grade_book_url_popup.title("成績表URL入力")
        # ?Bug from customtkinter
        self.after(
            200, lambda: self.set_icon(
                grade_book_url_popup, SHEET_ICON_LOCATION)
        )

        pop_width, pop_height, x_position, y_position = self.calculate_window_size(
            popup_width=520, popup_height=120
        )
        grade_book_url_popup.geometry(
            f"{pop_width}x{pop_height}+{x_position}+{y_position}"
        )

        ctk.CTkLabel(grade_book_url_popup, text="成績表URL:", font=self.font).grid(
            row=0, column=0, padx=(20, 0), pady=10, sticky="nw"
        )
        grade_book_url_entry = ctk.CTkEntry(
            grade_book_url_popup, width=300, font=self.font
        )
        grade_book_url_entry.grid(
            row=0, column=0, padx=(0, 20), pady=10, sticky="ne")

        # Load the grade book URL from the settings file
        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as settings_file:
            settings_data = json.load(settings_file)
        grade_book_url = settings_data["grade_book_url"]

        grade_book_url_entry.insert(0, grade_book_url)

        self.add_save_cancel_buttons(
            grade_book_url_popup,
            1,
            0,
            command=lambda: self.save_grade_book_url(
                grade_book_url_entry.get(), grade_book_url_popup
            ),
        )

        # Configure the rows and columns to have weight for scaling
        grade_book_url_popup.grid_rowconfigure(0, weight=1)
        grade_book_url_popup.grid_rowconfigure(1, weight=1)
        grade_book_url_popup.grid_columnconfigure(0, weight=1)

        grade_book_url_popup.grab_set()

    def enter_line_confidential(self) -> None:
        """Display a popup to enter LINE confidential information popup."""
        line_confidential_popup = ctk.CTkToplevel(self)
        line_confidential_popup.title("LINE機密情報入力")
        # line_confidential_popup.resizable(False, False)

        # ?Bug from customtkinter
        self.after(
            200, lambda: self.set_icon(
                line_confidential_popup, LINE_ICON_LOCATION)
        )

        # Calculate the position for the center of the main window
        popup_width, popup_height, x_position, y_position = self.calculate_window_size(
            popup_width=520, popup_height=180
        )

        # Set the position and dimensions of the popup
        line_confidential_popup.geometry(
            f"{popup_width}x{popup_height}+{x_position}+{y_position}"
        )

        # Add a "Channel Access Token" label and entry
        ctk.CTkLabel(
            line_confidential_popup, text="CHANNEL_ACCESS_TOKEN:", font=self.font
        ).grid(row=0, column=0, padx=15, pady=10, sticky="nw")
        channel_access_token_entry = ctk.CTkEntry(
            line_confidential_popup, width=200, font=self.font
        )
        channel_access_token_entry.grid(
            row=0, column=0, padx=(0, 15), pady=10, sticky="ne"
        )

        # Add a "User ID" label and entry
        ctk.CTkLabel(line_confidential_popup, text="USER_ID:", font=self.font).grid(
            row=1, column=0, padx=(15, 0), pady=10, sticky="sw"
        )
        user_id_entry = ctk.CTkEntry(
            line_confidential_popup, width=200, font=self.font)
        user_id_entry.grid(row=1, column=0, padx=(0, 15), pady=10, sticky="se")
        self.add_save_cancel_buttons(
            line_confidential_popup,
            2,
            0,
            command=lambda: self.save_line_confidential(
                channel_access_token_entry.get(),
                user_id_entry.get(),
                line_confidential_popup,
            ),
        )

        # Configure the rows and columns to have weight for scaling
        line_confidential_popup.grid_rowconfigure(0, weight=1)
        line_confidential_popup.grid_rowconfigure(1, weight=1)
        line_confidential_popup.grid_rowconfigure(2, weight=1)
        line_confidential_popup.grid_columnconfigure(0, weight=1)

        line_confidential_popup.grab_set()

    def save_grade_book_url(self, grade_book_url: str, grade_book_url_popup) -> None:
        """Save the entered URL to a JSON file."""
        # Read the existing JSON file
        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)

        # Update the JSON object with the new URL
        data["grade_book_url"] = grade_book_url

        # Write the updated JSON object back to the file
        with open(SETTINGS_FILE_LOCATION, "w", encoding="utf-8") as settings_file:
            json.dump(data, settings_file, ensure_ascii=False, indent=4)

        self.url_line_confidential_saved_label.configure(
            text="成績表URLの保存は成功しました！", font=self.font
        )
        self.after(
            4000, lambda: self.url_line_confidential_saved_label.configure(
                text="")
        )

        grade_book_url_popup.destroy()

    def save_line_confidential(
        self, channel_access_token: str, user_id: str, line_confidential_popup
    ) -> None:
        """Save the LINE confidential information to a file."""
        confidential_data = {
            "channel_access_token": channel_access_token,
            "user_id": user_id,
        }

        with open(TOKEN_ID_LOCATION, "w", encoding="utf-8") as config_file:
            json.dump(confidential_data, config_file, indent=4)

        self.url_line_confidential_saved_label.configure(
            text="機密情報の保存は成功しました！", font=self.font
        )
        self.after(
            4000, lambda: self.url_line_confidential_saved_label.configure(
                text="")
        )

        line_confidential_popup.destroy()

    def change_scaling_event(self, new_scaling: str) -> None:
        """Change the scaling when the OptionMenu value is changed"""
        new_scaling_float = int(new_scaling.strip("%")) / 100
        ctk.set_widget_scaling(new_scaling_float)

        # Remove the unwanted widgets (bugs)
        self.toggle_send_to_all_label()
        self.toggle_datetime_display()

    def show_saved_label(self) -> None:
        """Display a 'Saved!' label for 4 seconds."""
        saved_label = ctk.CTkLabel(
            self.settings, text="保存しました！", font=self.font)
        saved_label.grid(row=6, column=0, padx=(170, 0), pady=20, sticky="sw")
        self.settings.after(3000, lambda: saved_label.configure(text=""))

    @staticmethod
    def remove_saved_label(saved_label: ctk.CTkLabel) -> None:
        """Remove the 'Saved!' label from the grid."""
        saved_label.grid_remove()


class AppFrame(ctk.CTk):
    """The main application window."""

    def __init__(self) -> None:
        self.broadcast_bool = None
        self.total_ids = None
        self.current_index = None
        self.quiz_generation_thread = None
        self.blinking_task = None
        self.dot_counter = 0
        self.theme = self.read_settings()[0]
        self.button_color = self.read_settings()[1]
        self.scaling = int(self.read_settings()[2].strip("%")) / 100
        ctk.set_appearance_mode(self.theme)
        ctk.set_widget_scaling(self.scaling)
        ctk.set_default_color_theme(self.button_color)

        super().__init__()
        # Check if the application is running as a script or a packaged executable
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS  # type: ignore
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        # Get the correct icon path based on the application path
        icon_path = os.path.join(application_path, NHK_ICON_LOCATION)

        try:
            self.iconbitmap(icon_path)
        except TclError:
            print("Error: Unable to set the window icon.")
            pass

        self.title(f"NHK NEWS EASY 日本語クイズ作成 GUI {VERSION}")
        self.font = ctk.CTkFont(family="Yu Gothic UI", size=15)

        # Create a label to display the date and time
        self.datetime_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.datetime_label.grid(
            row=3, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.update_datetime_label()

        # *全員に発信ON時のラベル Label
        self.broadcast_on_label = ctk.CTkLabel(
            master=self, text=" ※全員に発信ON ", font=self.font
        )
        self.broadcast_on_label.grid(
            row=2, column=0, padx=(0, 20), pady=0, sticky="e")

        # Create the quiz type dropdown
        self.quiz_type_label = ctk.CTkLabel(
            master=self, text="クイズタイプ:", font=self.font)
        self.quiz_type_label.grid(
            row=0, column=0, padx=(20, 0), pady=10, sticky="nw")

        self.quiz_type_dropdown = ctk.CTkOptionMenu(
            master=self, values=["単語意味クイズ", "読み方クイズ"], font=self.font
        )
        self.quiz_type_dropdown.grid(
            row=0, column=0, padx=(120, 10), pady=10, sticky="nw"
        )

        # Create the number of questions entry
        self.label_number = ctk.CTkLabel(
            master=self, text="最大問題数:", font=self.font)
        self.label_number.grid(row=1, column=0, padx=(
            20, 0), pady=10, sticky="w")
        self.quiz_number_entry = ctk.CTkEntry(
            master=self, font=self.font, width=32)
        self.quiz_number_entry.grid(
            row=1, column=0, padx=(120, 0), pady=10, sticky="nw"
        )

        # Create the checkbox for instant LINE push
        self.instant_push_check_box = ctk.CTkCheckBox(
            master=self, text="すぐLINEに発信", font=self.font
        )
        self.instant_push_check_box.grid(
            row=2, column=0, padx=20, pady=10, sticky="w")

        # *Create the tab view instance
        self.tab_view = MainTab(
            master=self,
            datetime_label=self.datetime_label,
            quiz_type_dropdown=self.quiz_type_dropdown,
            quiz_number_entry=self.quiz_number_entry,
            instant_push_check_box=self.instant_push_check_box,
            broadcast_on_label=self.broadcast_on_label,
            width=860,
            height=300,
        )
        self.tab_view.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        self.load_saved_settings()

        # Set initial window size
        if self.tab_view.maximize_screen_check_box.get():
            self.after_idle(lambda: self.state("zoomed"))
            self.focus_force()
        else:
            self.after_idle(lambda: self.geometry("1220x754"))
            self.focus_force()

        # Create feedback message label
        self.feedback_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.feedback_label.grid(
            row=1, column=0, padx=(0, 20), pady=10, sticky="ne")

        # Create the progress bar label
        self.label_progress = ctk.CTkLabel(
            master=self, text="プログレス:", font=self.font)
        self.label_progress.grid(
            row=0, column=0, padx=(440, 0), pady=10, sticky="wn")

        # Create the progress bar
        self.progressbar = ctk.CTkProgressBar(
            master=self, width=270, height=20)
        self.progressbar.grid(row=0, column=0, padx=(
            535, 0), pady=15, sticky="wn")
        self.progressbar.set(0)

        # Create progress text label
        self.progress_text_label = ctk.CTkLabel(
            master=self, text="", font=self.font)
        self.progress_text_label.grid(
            row=1, column=0, padx=(535, 0), pady=10, sticky="wn"
        )

        # Create the reset button
        self.reset_button = ctk.CTkButton(
            master=self, text="やり直す", font=self.font, command=self.start_over
        )
        self.reset_button.grid(
            row=0, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.reset_button.configure(state="disabled")

        # Create the increment and decrement buttons
        self.increment_button = ctk.CTkButton(master=self, text="▲", width=30)
        self.increment_button.grid(
            row=1, column=0, padx=(165, 0), pady=10, sticky="w")
        self.decrement_button = ctk.CTkButton(master=self, text="▼", width=30)
        self.decrement_button.grid(
            row=1, column=0, padx=(205, 0), pady=10, sticky="w")
        self.increment_button.configure(command=self.increment_questions)
        self.decrement_button.configure(command=self.decrement_questions)

        # Create the make quiz button
        self.generate_quiz_button = ctk.CTkButton(
            master=self, text="クイズ作成", font=self.font, width=120
        )
        self.generate_quiz_button.grid(
            row=3, column=0, padx=20, pady=10, sticky="w")
        self.generate_quiz_button.configure(
            command=self.start_quiz_generation_thread)

        # Create the send quiz button
        self.send_quiz_button = ctk.CTkButton(
            master=self, text="LINEに発信", font=self.font, width=120
        )
        self.send_quiz_button.grid(
            row=3, column=0, padx=160, pady=10, sticky="nw")
        self.send_quiz_button.configure(command=self.press_push_quiz_button)
        self.send_quiz_button.configure(state="disabled")

        # Create the grade book button
        self.button_grade = ctk.CTkButton(
            master=self,
            text="成績表URL",
            command=self.open_grade_book,
            font=self.font,
            width=120,
        )
        self.button_grade.grid(row=3, column=0, padx=300, pady=10, sticky="nw")

        # News URL button
        self.open_news_url_button = ctk.CTkButton(
            master=self,
            text="📰ニュースURL",
            command=self.open_news_url,
            font=self.font,
            width=120,
        )
        self.open_news_url_button.grid(
            row=3, column=0, padx=440, pady=10, sticky="nw")
        self.open_news_url_button.configure(state="disabled")

        # Configure the grid
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def open_news_url(self) -> None:
        """Open the news URL."""
        with open(LOG_LOCATION, "r", encoding="utf-8") as log_file:
            news_url = log_file.readlines()[1]
        open_new_tab(news_url)

    @staticmethod
    def open_grade_book() -> None:
        """Open the grade book."""
        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as settings_file:
            settings_data = json.load(settings_file)

        # Extract the grade_book_url value from the JSON data
        grade_book_url = settings_data["grade_book_url"]
        open_new_tab(grade_book_url)

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
            self.open_news_url_button.configure(state="disabled")
            self.feedback_label.configure(text="")
            if self.quiz_number_entry.get() <= "0":
                self.show_feedback_label("最大問題数を指定してください。")
                sys.exit(1)

            self.broadcast_bool = bool(self.tab_view.broadcast_switch.get())
            self.emotion_analysis_bool = bool(
                self.tab_view.emotion_analysis_switch.get()
            )

            if self.instant_push_check_box.get() == 1:
                self.quiz_type_dropdown.configure(state="disabled")

            self.progress_text_label.configure(text="初期化中")
            self.blink_progress_text_label()

            # *Run the main function from the main module
            main(
                self.quiz_type_dropdown.get(),
                push=bool(self.instant_push_check_box.get()),
                questions=int(self.quiz_number_entry.get()),
                emotion=self.emotion_analysis_bool,
                broadcasting=self.broadcast_bool,
                progress_callback=self.update_progressbar,
            )

            # Update the progress bar and text label
            if not bool(self.instant_push_check_box.get()):
                self.show_feedback_label("作成完了(発信前にクイズの編集は可能)！")
                self.send_quiz_button.configure(state="normal")
            else:
                self.show_feedback_label("作成完了！LINEに送信済み！")
                self.send_quiz_button.configure(state="disabled")

            # Automatically update the text widget after quiz generation
            self.update_textboxes()

            # Enable buttons
            self.reset_button.configure(state="normal")
            self.quiz_type_dropdown.configure(state="normal")

        # Handle errors
        except ValueError:
            self.error_handler("最大問題数を指定してください。")
        except ConnectionError:
            self.error_handler("インターネット接続を確認してください。")
        except PermissionError:
            self.error_handler("LINEのTOKENを確認してください。")
        except RuntimeError:
            with open(LOG_LOCATION, "r", encoding="utf-8") as log_file:
                link_not_found_error = log_file.readlines()[1]
            self.error_handler(f"{link_not_found_error}")
        finally:
            self.tab_view.set("ファイル表示")
            if "エラー" in self.feedback_label.cget("text"):
                self.tab_view.sub_txt_tabs.set("ログファイル")
            elif self.quiz_type_dropdown.get() == "単語意味クイズ":
                self.tab_view.sub_txt_tabs.set("単語意味クイズ")
            else:
                self.tab_view.sub_txt_tabs.set("読み方クイズ")
            self.progressbar.stop()
            self.generate_quiz_button.configure(state="normal")
            self.instant_push_check_box.configure(state="normal")
            self.quiz_number_entry.configure(state="normal")
            self.increment_button.configure(state="normal")
            self.decrement_button.configure(state="normal")
            self.progress_text_label.configure(text="")
            self.open_news_url_button.configure(state="normal")

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
        """Reload the quiz text and push it to LINE."""
        def_quiz = self.tab_view.textboxes["単語意味クイズ"].get("1.0", ctk.END)
        with open(DEF_QUIZ_LOCATION, "w", encoding="utf-8") as f:
            f.write(def_quiz)

        pronoun_quiz = self.tab_view.textboxes["読み方クイズ"].get("1.0", ctk.END)
        with open(PRONOUN_QUIZ_LOCATION, "w", encoding="utf-8") as f:
            f.write(pronoun_quiz)

        # Switch to the log file tab
        self.tab_view.set("ファイル表示")
        self.tab_view.sub_txt_tabs.set("ログファイル")

        try:
            if self.quiz_type_dropdown.get() == "読み方クイズ":
                push_quiz(PRONOUN_QUIZ_LOCATION)
            else:
                push_quiz(DEF_QUIZ_LOCATION)
        except PermissionError:
            self.error_handler("LINEのTOKENを確認してください。")
        except IndexError:
            self.error_handler('クイズ中の"---"は削除しないでください。')
        except ConnectionError:
            self.error_handler("インターネット接続を確認してください。")
        else:
            self.feedback_label.configure(text="LINEに送信しました！")
            with open(LOG_LOCATION, "a+", encoding="utf-8") as f:
                f.write("送信済み\n")
                f.seek(0)
                url = f.readlines()[1]
            save_quiz_vocab(url)
            self.update_textboxes()
            self.send_quiz_button.configure(state="disabled")

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
        self.tab_view.set("ファイル表示")
        self.tab_view.sub_txt_tabs.set("ログファイル")
        self.quiz_number_entry.delete(0, ctk.END)
        self.generate_quiz_button.configure(state="normal")
        self.send_quiz_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        self.open_news_url_button.configure(state="disabled")
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
        if os.path.exists(SETTINGS_FILE_LOCATION):
            with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as file:
                saved_settings = json.load(file)
                self.tab_view.update_settings(saved_settings)

    @staticmethod
    def read_settings() -> Tuple[str, ...]:
        """Read the settings from a file."""
        if not os.path.exists(SETTINGS_FILE_LOCATION):
            create_default_settings_file()

        with open(SETTINGS_FILE_LOCATION, "r", encoding="utf-8") as file:
            settings = json.load(file)
            theme = settings.get("theme")
            button_color = settings.get("button_color")
            scaling = settings.get("scaling")
            return theme, button_color, scaling

    def update_datetime_label(self) -> None:
        """Update the date and time label with the current date and time."""

        def weekday_in_jp(weekday: int) -> str:
            japanese_weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            return japanese_weekdays[weekday]

        # Update the date and time label
        now = datetime.now()
        current_time = now.strftime(
            f"%Y-%m-%d ({weekday_in_jp(now.weekday())}) %H:%M:%S"
        )
        self.datetime_label.configure(text=current_time)
        self.after(1000, self.update_datetime_label)

    def show_feedback_label(self, text) -> None:
        """Show the success label."""
        self.feedback_label.configure(text=text)

    def blink_progress_text_label(self) -> None:
        """Blink the progress text label."""
        if self.blinking_task:
            self.after_cancel(self.blinking_task)

        if (
            self.current_index == 0
            and self.feedback_label
            and "エラー" not in self.feedback_label.cget("text")
        ):
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
            self.blinking_task = self.after(
                500, self.blink_progress_text_label)
        elif self.generate_quiz_button.cget(
            "state"
        ) == "disabled" and "エラー" not in self.feedback_label.cget("text"):
            base_text = f"クイズを作成中({self.current_index}/{self.total_ids})"

            dots = (
                "・" * self.dot_counter
            )  # Generate dots based on the dot_counter value
            new_text = base_text + dots
            self.progress_text_label.configure(text=new_text)

            # Cycle through 0, 1, 2, 3 for the dot_counter
            dot_counter = (self.dot_counter + 1) % 4
            self.dot_counter = dot_counter
            self.blinking_task = self.after(
                2000, self.blink_progress_text_label)
        else:
            self.progress_text_label.configure(text="")

    def error_handler(self, error_text: str) -> None:
        """Handle errors."""
        self.progress_text_label.configure(text="")
        self.feedback_label.configure(text=f"エラー：{error_text}")
        self.reset_button.configure(state="normal")
        self.generate_quiz_button.configure(state="normal")


if __name__ == "__main__":
    app = AppFrame()
    app.mainloop()
