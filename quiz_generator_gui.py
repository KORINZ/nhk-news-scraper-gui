import tkinter as tk
from tkinter import messagebox
from main import main, push_quiz
import tkinter.ttk as ttk
import threading

import os
from tkinter import filedialog

VERSION = "v1.0.0"
PRONOUN_QUIZ_LOCATION = r'./pronunciation_quiz.txt'
DEF_QUIZ_LOCATION = r'./definition_quiz.txt'
is_blinking = False


def save_text_to_file() -> None:
    """Save the content of the Text widget to a file."""
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not file_path:
        return

    content = article_text.get("1.0", tk.END)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def start_over() -> None:
    """Reset the app to its initial state."""
    article_text.delete("1.0", tk.END)
    questions_entry.delete(0, tk.END)
    questions_entry.insert(0, "5")
    test_type_combobox.current(1)
    line_push_var.set(False)
    load_article_button.config(state="disabled")
    load_def_quiz_button.config(state="disabled")
    load_pron_quiz_button.config(state="disabled")
    load_log_button.config(state="disabled")
    send_button.config(state="disabled")


def enter_line_confidential() -> None:
    """Display a popup to enter LINE confidential information."""
    line_confidential_popup = tk.Toplevel(root)
    line_confidential_popup.title("LINE機密情報入力")
    line_confidential_popup.iconbitmap(r'icon/LINE.ico')

    tk.Label(line_confidential_popup, text="CHANNEL_ACCESS_TOKEN:").grid(
        row=0, column=0, sticky="w")
    channel_access_token_entry = tk.Entry(line_confidential_popup)
    channel_access_token_entry.grid(
        row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(line_confidential_popup, text="USER_ID:").grid(
        row=1, column=0, sticky="w")
    user_id_entry = tk.Entry(line_confidential_popup)
    user_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    save_button = tk.Button(line_confidential_popup, text="保存", command=lambda: save_line_confidential(
        channel_access_token_entry.get(), user_id_entry.get()))
    save_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    # Add a "Cancel" button
    cancel_button = tk.Button(
        line_confidential_popup, text="キャンセル", command=line_confidential_popup.destroy)
    cancel_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")


def save_line_confidential(channel_access_token: str, user_id: str) -> None:
    """Save the LINE confidential information to a config.py file."""
    with open("config.py", "w", encoding="utf-8") as config_file:
        config_file.write(f"CHANNEL_ACCESS_TOKEN = '{channel_access_token}'\n")
        config_file.write(f"USER_ID = '{user_id}'\n")
    messagebox.showinfo("成功", "LINE機密情報が保存されました！")


def show_credit_popup() -> None:
    """Display a popup with the version number and credit information."""
    credit_info = "バージョン: " + VERSION + "\n開発者: KORIN\n年: 2023"
    messagebox.showinfo("クレジット", credit_info)


def start_quiz_generation_thread() -> None:
    """Start a thread to run the quiz generation function in the background."""
    global is_blinking
    is_blinking = True
    status_label.config(text="何も押さないでください。クイズ作成中")
    update_status_label_blink()
    quiz_generation_thread = threading.Thread(target=run_quiz_generation)
    quiz_generation_thread.start()


def run_quiz_generation() -> None:
    """Run the quiz generation function in the background."""
    global is_blinking
    try:
        main(test_type_var.get(), push=line_push_var.get(),
             questions=int(questions_var.get()))
        messagebox.showinfo("成功", "クイズ生成が完了しました！")
        # Automatically update the Text widget after quiz generation
        load_file('news_article.txt')
        send_button.config(state="normal")  # Enable the send button
        # Enable the file load buttons
        load_article_button.config(state="normal")
        load_def_quiz_button.config(state="normal")
        load_pron_quiz_button.config(state="normal")
        load_log_button.config(state="normal")
        is_blinking = False
        status_label.config(text="")
    except ValueError:
        messagebox.showerror("エラー", "問題数を指定してください。")
        is_blinking = False
        status_label.config(text="")


def press_push_quiz_button() -> None:
    """Send the quiz to LINE."""
    try:
        if test_type_var.get() == "読み方クイズ":
            push_quiz(PRONOUN_QUIZ_LOCATION)
        else:
            push_quiz(DEF_QUIZ_LOCATION)
        messagebox.showinfo("成功", "クイズを発信しました！")
    except Exception as e:
        messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")


def load_file(file_name: str) -> None:
    """Load a file into the Text widget."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            content = file.read()
            article_text.delete("1.0", tk.END)
            article_text.insert(tk.END, content)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_name}' not found.")


def update_status_label_blink() -> None:
    """Update the status label to blink."""
    global is_blinking
    if not is_blinking:
        return

    current_text = status_label.cget("text")
    if current_text == "何も押さないでください。クイズ作成中":
        new_text = "何も押さないでください。クイズ作成中・"
    elif current_text == "何も押さないでください。クイズ作成中・":
        new_text = "何も押さないでください。クイズ作成中・・"
    elif current_text == "何も押さないでください。クイズ作成中・・":
        new_text = "何も押さないでください。クイズ作成中・・・"
    else:
        new_text = "何も押さないでください。クイズ作成中"

    status_label.config(text=new_text)
    root.after(750, update_status_label_blink)  # Schedule the next update


root = tk.Tk()
root.title(f'NHK NEWS EASY クイズ作成 GUI {VERSION}')
root.geometry("970x600")
root.option_add("*font", "Mincho, 12")
root.iconbitmap(r'icon/nhk.ico')

status_label = tk.Label(root, text="")
status_label.grid(row=3, column=1, padx=(230, 0), sticky="w")

test_type_var = tk.StringVar()
line_push_var = tk.BooleanVar()
questions_var = tk.StringVar()


# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="ファイル", menu=file_menu)

# Add a "Save As" option to the "File" menu
file_menu.add_command(label="表示しているファイル名前を付けて保存", command=save_text_to_file)

# Create a "Tool" menu
tool_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="ツール", menu=tool_menu)

# Add a "Start Over" option to the "Tool" menu
tool_menu.add_command(label="やり直し", command=start_over)

# Add an "Enter LINE Confidential" option to the "Tool" menu
tool_menu.add_command(label="LINE機密情報入力", command=enter_line_confidential)

# Create an "About" menu
about_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="情報", menu=about_menu)

# Add a "Credit" option to the "About" menu
about_menu.add_command(
    label=f"NHK NEWS EASY クイズ作成 GUI {VERSION}について", command=show_credit_popup)


# Set the default value for test_type_var
test_type_var.set("単語意味クイズ")

test_type_label = tk.Label(root, text="クイズタイプ:")
test_type_label.grid(row=0, column=0, sticky="w")

# Create a ttk.Combobox to replace the OptionMenu
test_type_combobox = ttk.Combobox(root, textvariable=test_type_var, values=[
                                  "読み方クイズ", "単語意味クイズ"], state="readonly")
test_type_combobox.grid(row=0, column=1, sticky="w")


line_push_label = tk.Label(root, text="すぐLINEに発信:")
line_push_label.grid(row=1, column=0, sticky="w")
line_push_check = tk.Checkbutton(root, variable=line_push_var)
line_push_check.grid(row=1, column=1, sticky="w")

questions_label = tk.Label(root, text="最大問題数:")
questions_label.grid(row=2, column=0, sticky="w")
questions_entry = tk.Entry(root, textvariable=questions_var, width=4)
questions_entry.insert(0, "5")
questions_entry.grid(row=2, column=1, sticky="w")

generate_button = tk.Button(
    root, text="クイズ作成", command=start_quiz_generation_thread)
generate_button.grid(row=3, column=1, pady=(10, 20), sticky="w")

send_button = tk.Button(
    root, text="LINEに発信", command=press_push_quiz_button, state="disabled")  # Disable the send button initially
send_button.grid(row=3, column=1, padx=(110, 0), pady=(10, 20), sticky="w")

article_label = tk.Label(root, text="ファイル表示:")
article_label.grid(row=4, column=0, sticky="w")

article_text = tk.Text(root, wrap=tk.WORD)
article_text.grid(row=5, column=0, columnspan=2,
                  padx=10, pady=10, sticky="nsew")

scrollbar = tk.Scrollbar(root, command=article_text.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
article_text.config(yscrollcommand=scrollbar.set)

load_article_button = tk.Button(
    root, text="ニュース文章", command=lambda: load_file("news_article.txt"), state="disabled")
load_article_button.grid(row=4, column=1, sticky="w")

load_def_quiz_button = tk.Button(
    root, text="単語意味クイズ", command=lambda: load_file("definition_quiz.txt"), state="disabled")
load_def_quiz_button.grid(row=4, column=1, padx=(125, 0), sticky="w")

load_pron_quiz_button = tk.Button(
    root, text="読み方クイズ", command=lambda: load_file("pronunciation_quiz.txt"), state="disabled")
load_pron_quiz_button.grid(row=4, column=1, padx=(265, 0), sticky="w")

load_log_button = tk.Button(
    root, text="ログファイル", command=lambda: load_file("log.txt"), state="disabled")
load_log_button.grid(row=4, column=1, padx=(390, 0), sticky="w")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(5, weight=1)

root.mainloop()
