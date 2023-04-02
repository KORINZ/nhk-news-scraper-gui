import customtkinter
import threading
from main import main, push_quiz
from tkinter import messagebox
import sys

VERSION = "v0.0.2b"
customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("dark")

DEFAULT_NUMBER_OF_QUESTIONS = "4"

PRONOUN_QUIZ_LOCATION = r'txt_files/pronunciation_quiz.txt'
DEF_QUIZ_LOCATION = r'txt_files/definition_quiz.txt'
LOG_LOCATION = r'txt_files/push_log.txt'
NEWS_ARTICLE_LOCATION = r'txt_files/news_article.txt'
NHK_ICON_LOCATION = r'./icon/nhk.ico'


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.font = customtkinter.CTkFont(family="Yu Gothic UI", size=16)
        self._segmented_button.configure(font=self.font)

        # *ファイル Tab
        self.add("ファイル表示")
        self.sub_txt_tabs = customtkinter.CTkTabview(
            master=self.tab("ファイル表示"))
        self.sub_txt_tabs.pack(fill="both", expand=True)
        self.sub_txt_tabs._segmented_button.configure(
            font=self.font)
        self.textboxes = {}

        def create_txt_tab(self, tab_name, txt_file) -> None:
            """Create sub-tabs with textboxes that display the contents of txt files"""
            self.sub_txt_tabs.add(tab_name)
            self.frame = customtkinter.CTkFrame(
                master=self.sub_txt_tabs.tab(tab_name))

            self.frame.pack(fill="both", expand=True)

            self.textbox = customtkinter.CTkTextbox(
                master=self.frame, wrap=customtkinter.WORD, font=self.font)
            self.textbox.pack(fill="both", expand=True)

            if tab_name == "ログファイル":
                with open(txt_file, 'r', encoding='utf-8') as f:
                    self.textbox.insert('insert', f.read())
            # Store the textbox in the dictionary
            self.textboxes[tab_name] = self.textbox

        # add widgets on tabs in nested Tabview
        create_txt_tab(self, "ニュース文章", NEWS_ARTICLE_LOCATION)
        create_txt_tab(self, "単語意味クイズ", DEF_QUIZ_LOCATION)
        create_txt_tab(self, "読み方クイズ", PRONOUN_QUIZ_LOCATION)
        create_txt_tab(self, "ログファイル", LOG_LOCATION)

        # *設定 Tab
        self.add("設定")
        self.settings = customtkinter.CTkFrame(master=self.tab("設定"))
        self.settings.pack(fill="both", expand=True)
        # Settings tab
        self.label_theme = customtkinter.CTkLabel(
            master=self.settings, text="テーマ:", font=self.font)
        self.label_theme.grid(row=0, column=0, padx=(
            20, 0), pady=20, sticky="nw")
        self.optionmenu_var = customtkinter.StringVar(value="Dark")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.settings,
                                                                       values=[
                                                                           "Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event,
                                                                       variable=self.optionmenu_var)
        self.appearance_mode_optionemenu.grid(
            row=0, column=0, padx=(100, 0), pady=20, sticky="nw")

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        customtkinter.set_appearance_mode(new_appearance_mode)


class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1000x618")
        # self.resizable(False, False)
        self.iconbitmap(NHK_ICON_LOCATION)
        self.title(f'NHK NEWS EASY クイズ作成 CTk GUI {VERSION}')

        self.font = customtkinter.CTkFont(family="Yu Gothic UI", size=16)

        # Create the test type radio buttons
        # ? self.line_push_var = tk.BooleanVar()

        # Create the progress bar
        self.label_progress = customtkinter.CTkLabel(
            master=self, text="プログレス:", font=self.font)
        self.label_progress.grid(
            row=0, column=0, padx=(0, 450), pady=10, sticky="ne")

        self.progressbar = customtkinter.CTkProgressBar(
            master=self, width=250, height=20)
        self.progressbar.grid(row=0, column=0, padx=(
            0, 180), pady=15, sticky="ne")
        self.progressbar.set(0)

        self.reset_button = customtkinter.CTkButton(
            master=self, text="やり直す", font=self.font, command=self.start_over)
        self.reset_button.grid(
            row=0, column=0, padx=(0, 20), pady=10, sticky="ne")
        self.reset_button.configure(state="disabled")

        self.label_type = customtkinter.CTkLabel(
            master=self, text="クイズタイプ:", font=self.font)
        self.label_type.grid(row=0, column=0, padx=(
            20, 0), pady=10, sticky="nw")

        self.combobox = customtkinter.CTkComboBox(
            master=self, values=["単語意味クイズ", "読み方クイズ"], font=self.font)
        self.combobox.grid(row=0, column=0, padx=(
            120, 10), pady=10, sticky="nw")

        self.label_number = customtkinter.CTkLabel(
            master=self, text="最大問題数:", font=self.font)
        self.label_number.grid(
            row=1, column=0, padx=(20, 120), sticky="w")
        self.number_entry = customtkinter.CTkEntry(
            master=self, width=35, font=self.font)
        self.number_entry.grid(row=1, column=0, padx=(120, 0), sticky="nw")
        self.number_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)

        # Create the increment and decrement buttons
        self.increment_button = customtkinter.CTkButton(
            master=self, text="▲", width=30)
        self.increment_button.grid(
            row=1, column=0, padx=(160, 0), pady=(0, 0), sticky="w")
        self.decrement_button = customtkinter.CTkButton(
            master=self, text="▼", width=30)
        self.decrement_button.grid(
            row=1, column=0, padx=(200, 0), pady=(0, 0), sticky="w")
        self.increment_button.configure(command=self.increment_questions)
        self.decrement_button.configure(command=self.decrement_questions)

        self.check_box = customtkinter.CTkCheckBox(
            master=self, text="すぐLINEに発信", font=self.font)
        self.check_box.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # Create the make and send buttons
        self.button_make = customtkinter.CTkButton(
            master=self, text="クイズ作成", font=self.font)
        self.button_make.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.button_make.configure(command=self.start_quiz_generation_thread)

        self.button_send = customtkinter.CTkButton(
            master=self, text="LINEに発信", font=self.font)
        self.button_send.grid(row=3, column=0, padx=180, pady=10, sticky="nw")
        self.button_send.configure(command=self.press_push_quiz_button)
        self.button_send.configure(state="disabled")

        self.button_grade = customtkinter.CTkButton(
            master=self, text="成績チェック", font=self.font)
        self.button_grade.grid(row=3, column=0, padx=340, pady=10, sticky="nw")

        # Create the tab view
        self.tab_view = MyTabView(master=self, width=860, height=300)
        self.tab_view.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

        self.grid_rowconfigure(4, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

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
            main(self.combobox.get(), push=bool(self.check_box.get()),
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
            self.number_entry.delete(0, customtkinter.END)
            self.number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            self.number_entry.delete(0, customtkinter.END)
            self.number_entry.insert(0, str(current_value + 1))

    def decrement_questions(self) -> None:
        """Decrease the value of the questions Entry."""
        current_value_str = self.number_entry.get().strip()
        if not current_value_str.isdigit():
            self.number_entry.delete(0, customtkinter.END)
            self.number_entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            if current_value > 1:
                self.number_entry.delete(0, customtkinter.END)
                self.number_entry.insert(0, str(current_value - 1))

    def update_progressbar(self, progress: float) -> None:
        """Update the progressbar in the main window."""
        app.progressbar.set(progress)

    def press_push_quiz_button(self) -> None:
        """Send the quiz to LINE."""
        try:
            if self.combobox.get() == "読み方クイズ":
                push_quiz(PRONOUN_QUIZ_LOCATION)
            else:
                push_quiz(DEF_QUIZ_LOCATION)
            messagebox.showinfo("成功", "クイズを発信しました！")
            with open(LOG_LOCATION, 'a', encoding='utf-8') as f:
                f.write('PUSHED\n')
            self.update_textboxes()
        except PermissionError as e:
            messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")

    def update_textboxes(self, initial_load: bool = False) -> None:
        """Clear and update the textboxes after quiz generation."""
        file_tab_mapping = {
            "ニュース文章": NEWS_ARTICLE_LOCATION,
            "単語意味クイズ": DEF_QUIZ_LOCATION,
            "読み方クイズ": PRONOUN_QUIZ_LOCATION,
            "ログファイル": LOG_LOCATION,
        }

        for tab_name, file_location in file_tab_mapping.items():
            textbox = self.tab_view.textboxes[tab_name]

            # Clear the textbox content only if it's not the initial load and the tab is not "ログファイル"
            if not initial_load or tab_name != "ログファイル":
                textbox.delete("1.0", customtkinter.END)

            with open(file_location, "r", encoding="utf-8") as file:
                content = file.read()
                textbox.insert(customtkinter.END, content)

    def start_over(self) -> None:
        """Reset the app to its initial state."""
        self.number_entry.delete(0, customtkinter.END)
        self.number_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)
        self.combobox.set("単語意味クイズ")
        self.check_box.configure(state="normal")
        self.button_send.configure(state="disabled")
        self.progressbar.set(0)

        # Clear the textboxes (except the log file)
        for tab_name, textbox in self.tab_view.textboxes.items():
            if tab_name != "ログファイル":
                textbox.delete("1.0", customtkinter.END)


app = App()
app.mainloop()
