import tkinter as tk
from tkinter import messagebox
from main import main


def run_quiz_generation() -> None:
    try:
        main(test_type_var.get(), push=line_push_var.get(),
             questions=int(questions_var.get()))
        messagebox.showinfo("成功", "クイズ生成が完了しました！")
        # Automatically update the Text widget after quiz generation
        load_file('news_article.txt')
    except Exception:
        messagebox.showerror("エラー", "問題数を指定してください。")


def load_file(file_name: str) -> None:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            content = file.read()
            article_text.delete("1.0", tk.END)
            article_text.insert(tk.END, content)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_name}' not found.")


root = tk.Tk()
root.title("NHK NEWS EASY クイズ作成 GUI")
root.geometry("500x600")

test_type_var = tk.StringVar()
line_push_var = tk.BooleanVar()
questions_var = tk.StringVar()

# Set the default value for test_type_var
test_type_var.set("単語意味クイズ")

test_type_label = tk.Label(root, text="クイズタイプ:")
test_type_label.grid(row=0, column=0, sticky="w")
test_type_option = tk.OptionMenu(
    root, test_type_var, "読み方クイズ", "単語意味クイズ")
test_type_option.grid(row=0, column=1, sticky="w")

line_push_label = tk.Label(root, text="LINEに発信:")
line_push_label.grid(row=1, column=0, sticky="w")
line_push_check = tk.Checkbutton(root, variable=line_push_var)
line_push_check.grid(row=1, column=1, sticky="w")

questions_label = tk.Label(root, text="問題数:")
questions_label.grid(row=2, column=0, sticky="w")
questions_entry = tk.Entry(root, textvariable=questions_var, width=5)
questions_entry.grid(row=2, column=1, sticky="w")

generate_button = tk.Button(
    root, text="クイズ作成", command=run_quiz_generation)
generate_button.grid(row=3, column=1, pady=(10, 20), sticky="w")

article_label = tk.Label(root, text="ファイル表示:")
article_label.grid(row=4, column=0, sticky="w")

article_text = tk.Text(root, wrap=tk.WORD)
article_text.grid(row=5, column=0, columnspan=2,
                  padx=10, pady=10, sticky="nsew")

scrollbar = tk.Scrollbar(root, command=article_text.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
article_text.config(yscrollcommand=scrollbar.set)

load_article_button = tk.Button(
    root, text="ニュース文章", command=lambda: load_file("news_article.txt"))
load_article_button.grid(row=4, column=1, sticky="w")

load_def_quiz_button = tk.Button(
    root, text="単語意味クイズ", command=lambda: load_file("definition_quiz.txt"))
load_def_quiz_button.grid(row=4, column=1, padx=(80, 0), sticky="w")

load_pron_quiz_button = tk.Button(
    root, text="読み方クイズ", command=lambda: load_file("pronunciation_quiz.txt"))
load_pron_quiz_button.grid(row=4, column=1, padx=(180, 0), sticky="w")

load_log_button = tk.Button(
    root, text="ログファイル", command=lambda: load_file("log.txt"))
load_log_button.grid(row=4, column=1, padx=(265, 0), sticky="w")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(5, weight=1)

root.mainloop()
