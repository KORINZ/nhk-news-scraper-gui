import customtkinter

VERSION = "v0.0.1a"
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

        # Create Tab 1 and nested Tabview
        self.add("ファイル")
        self.nested_tab_view = customtkinter.CTkTabview(
            master=self.tab("ファイル"))
        self.nested_tab_view.pack(fill="both", expand=True)
        self.nested_tab_view._segmented_button.configure(
            font=self.font)  # Add this line

        # Create Tab 2
        self.add("設定")
        self.blank_frame = customtkinter.CTkFrame(master=self.tab("設定"))
        self.blank_frame.pack(fill="both", expand=True)

        # create tabs in nested Tabview
        def create_txt_tab(self, tab_name, txt_file) -> None:
            self.nested_tab_view.add(tab_name)
            self.frame = customtkinter.CTkFrame(
                master=self.nested_tab_view.tab(tab_name))

            self.frame.pack(fill="both", expand=True)

            self.textbox = customtkinter.CTkTextbox(
                master=self.frame, wrap=customtkinter.WORD, font=self.font)
            self.textbox.pack(fill="both", expand=True)

            with open(txt_file, 'r', encoding='utf-8') as f:
                self.textbox.insert('insert', f.read())

        # add widgets on tabs in nested Tabview
        create_txt_tab(self, "ニュース文章", NEWS_ARTICLE_LOCATION)
        create_txt_tab(self, "単語意味クイズ", DEF_QUIZ_LOCATION)
        create_txt_tab(self, "読み方クイズ", PRONOUN_QUIZ_LOCATION)
        create_txt_tab(self, "ログファイル", LOG_LOCATION)


class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1000x618")
        # self.resizable(False, False)
        self.iconbitmap(NHK_ICON_LOCATION)
        self.title(f'NHK NEWS EASY クイズ作成 CTk GUI {VERSION}')

        self.font = customtkinter.CTkFont(family="Yu Gothic UI", size=16)

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
        self.entry = customtkinter.CTkEntry(
            master=self, width=35, font=self.font)
        self.entry.grid(row=1, column=0, padx=(120, 0), sticky="nw")
        self.entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)

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

        self.button_make = customtkinter.CTkButton(
            master=self, text="クイズ作成", font=self.font)
        self.button_make.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.button_send = customtkinter.CTkButton(
            master=self, text="LINEに発信", font=self.font)
        self.button_send.grid(row=3, column=0, padx=180, pady=10, sticky="nw")

        self.tab_view = MyTabView(master=self, width=860, height=300)
        self.tab_view.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

        self.grid_rowconfigure(4, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

    def increment_questions(self) -> None:
        """Increase the value of the questions Entry."""
        current_value_str = self.entry.get().strip()
        if not current_value_str.isdigit():
            self.entry.delete(0, customtkinter.END)
            self.entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            self.entry.delete(0, customtkinter.END)
            self.entry.insert(0, str(current_value + 1))

    def decrement_questions(self) -> None:
        """Decrease the value of the questions Entry."""
        current_value_str = self.entry.get().strip()
        if not current_value_str.isdigit():
            self.entry.delete(0, customtkinter.END)
            self.entry.insert(0, "1")
        else:
            current_value = int(current_value_str)
            if current_value > 1:
                self.entry.delete(0, customtkinter.END)
                self.entry.insert(0, str(current_value - 1))


app = App()
app.mainloop()
