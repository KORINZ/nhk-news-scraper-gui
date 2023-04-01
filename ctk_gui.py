import customtkinter

customtkinter.set_appearance_mode("dark")

PRONOUN_QUIZ_LOCATION = r'txt_files/pronunciation_quiz.txt'
DEF_QUIZ_LOCATION = r'txt_files/definition_quiz.txt'
LOG_LOCATION = r'txt_files/push_log.txt'
NEWS_ARTICLE_LOCATION = r'txt_files/news_article.txt'
NHK_ICON_LOCATION = r'./icon/nhk.ico'


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        # create tabs

        def create_txt_tab(self, tab_name, txt_file) -> None:
            self.add(tab_name)
            self.label = customtkinter.CTkLabel(master=self.tab(tab_name))
            self.label.grid(row=0, column=0, padx=0, pady=0)
            self.textbox = customtkinter.CTkTextbox(
                master=self.label, width=860, height=300, font=customtkinter.CTkFont(family="Yu Gothic UI", size=16))
            self.textbox.grid(row=0, column=0, columnspan=2,
                              padx=0, pady=(0, 0), sticky="nsew")
            with open(txt_file, 'r', encoding='utf-8') as f:
                self.textbox.insert('insert', f.read())

        # add widgets on tabs
        create_txt_tab(self, "ニュース文章", NEWS_ARTICLE_LOCATION)
        create_txt_tab(self, "単語意味クイズ", DEF_QUIZ_LOCATION)
        create_txt_tab(self, "読み方クイズ", PRONOUN_QUIZ_LOCATION)
        create_txt_tab(self, "ログファイル", LOG_LOCATION)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x556")
        # self.resizable(False, False)
        self.iconbitmap(NHK_ICON_LOCATION)
        self.title("GUI demo")
        self.grid_rowconfigure(4, weight=1)  # configure grid system
        self.grid_columnconfigure(1, weight=1)

        my_font = customtkinter.CTkFont(family="Yu Gothic UI", size=16)

        self.label_type = customtkinter.CTkLabel(
            master=self, text="クイズタイプ:", font=my_font)
        self.label_type.grid(row=0, column=0, padx=(
            20, 0), pady=10, sticky="nw")

        self.combobox = customtkinter.CTkComboBox(
            master=self, values=["単語意味クイズ", "読み方クイズ"], font=my_font)
        self.combobox.grid(row=0, column=0, padx=(
            120, 10), pady=10, sticky="nw")

        self.label_number = customtkinter.CTkLabel(
            master=self, text="最大問題数:", font=my_font)
        self.label_number.grid(
            row=1, column=0, padx=(20, 120), sticky="w")
        self.entry = customtkinter.CTkEntry(
            master=self, width=35, font=my_font)
        self.entry.grid(row=1, column=0, padx=(120, 0), sticky="nw")

        # Create the increment and decrement buttons
        self.increment_button = customtkinter.CTkButton(
            master=self, text="▲", width=30)
        self.increment_button.grid(
            row=1, column=0, padx=(160, 0), pady=(0, 0), sticky="w")
        self.decrement_button = customtkinter.CTkButton(
            master=self, text="▼", width=30)
        self.decrement_button.grid(
            row=1, column=0, padx=(200, 0), pady=(0, 0), sticky="w")

        self.check_box = customtkinter.CTkCheckBox(
            master=self, text="すぐLINEに発信", font=my_font)
        self.check_box.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.button_make = customtkinter.CTkButton(
            master=self, text="クイズ作成", font=my_font)
        self.button_make.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.button_send = customtkinter.CTkButton(
            master=self, text="LINEに発信", font=my_font)
        self.button_send.grid(row=3, column=0, padx=180, pady=10, sticky="nw")

        self.tab_view = MyTabView(master=self, width=860, height=300)
        self.tab_view.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")


app = App()
app.mainloop()
