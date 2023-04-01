import tkinter as tk
from tkinter import messagebox
from main import main, push_quiz
import customtkinter as ctk
import threading

from tkinter import filedialog

# Global variables
VERSION = "v1.1.0"
DEFAULT_NUMBER_OF_QUESTIONS = "4"
PRONOUN_QUIZ_LOCATION = r'txt_files/pronunciation_quiz.txt'
DEF_QUIZ_LOCATION = r'txt_files/definition_quiz.txt'
LOG_LOCATION = r'txt_files/push_log.txt'
NEWS_ARTICLE_LOCATION = r'txt_files/news_article.txt'
LINE_ICON_LOCATION = r'./icon/LINE.ico'
NHK_ICON_LOCATION = r'./icon/nhk.ico'
is_blinking = False


def save_text_to_file() -> None:
    """Save the content of the Text widget to a file."""
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not file_path:
        return None

    content = article_text.get("1.0", tk.END)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def start_over() -> None:
    """Reset the app to its initial state."""
    article_text.delete("1.0", tk.END)
    questions_entry.delete(0, tk.END)
    questions_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)
    # test_type_combobox.current(1)
    line_push_var.set(False)
    load_article_button.configure(state="disabled")
    load_def_quiz_button.configure(state="disabled")
    load_pron_quiz_button.configure(state="disabled")
    send_button.configure(state="disabled")


def enter_line_confidential() -> None:
    """Display a popup to enter LINE confidential information."""
    line_confidential_popup = ctk.CTkToplevel(root)
    line_confidential_popup.title("LINE機密情報入力")
    line_confidential_popup.iconbitmap(LINE_ICON_LOCATION)

    # Calculate the position for the center of the main window
    main_window_width = root.winfo_width()
    main_window_height = root.winfo_height()
    main_window_x = root.winfo_x()
    main_window_y = root.winfo_y()
    popup_width = 420
    popup_height = 105
    x_position = main_window_x + (main_window_width // 2) - (popup_width // 2)
    y_position = main_window_y + \
        (main_window_height // 2) - (popup_height // 2)

    # Set the position and dimensions of the popup
    line_confidential_popup.geometry(
        f"{popup_width}x{popup_height}+{x_position}+{y_position}")

    # Add a "Channel Access Token" label and entry
    ctk.CTkLabel(line_confidential_popup, text="CHANNEL_ACCESS_TOKEN:").grid(
        row=0, column=0, sticky="w")
    channel_access_token_entry = ctk.CTkEntry(line_confidential_popup)
    channel_access_token_entry.grid(
        row=0, column=1, padx=5, pady=5, sticky="w")

    # Add a "User ID" label and entry
    ctk.CTkLabel(line_confidential_popup, text="USER_ID:").grid(
        row=1, column=0, sticky="w")
    user_id_entry = ctk.CTkEntry(line_confidential_popup)
    user_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Add a "Save" button
    save_button = ctk.CTkButton(line_confidential_popup, text="保存", command=lambda: save_line_confidential(
        channel_access_token_entry.get(), user_id_entry.get(), line_confidential_popup))
    save_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    # Add a "Cancel" button
    cancel_button = ctk.CTkButton(
        line_confidential_popup, text="キャンセル", command=line_confidential_popup.destroy)
    cancel_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")


def save_line_confidential(channel_access_token: str, user_id: str, line_confidential_popup: tk.Toplevel) -> None:
    """Save the LINE confidential information to a config.py file."""
    with open("config.py", "w", encoding="utf-8") as config_file:
        config_file.write(f"CHANNEL_ACCESS_TOKEN = '{channel_access_token}'\n")
        config_file.write(f"USER_ID = '{user_id}'\n")
    messagebox.showinfo("成功", "LINE機密情報が保存されました！\nGUIを再起動してください。")
    line_confidential_popup.destroy()


def show_credit_popup() -> None:
    """Display a popup with the version number and credit information."""
    credit_info = "バージョン: " + VERSION + "\n開発者: KORIN\n年: 2023"
    messagebox.showinfo("クレジット", credit_info)


def start_quiz_generation_thread() -> None:
    """Start a thread to run the quiz generation function in the background."""
    global is_blinking
    is_blinking = True
    status_label.configure(text="")
    update_status_label_blink()
    quiz_generation_thread = threading.Thread(target=run_quiz_generation)
    quiz_generation_thread.start()


def run_quiz_generation() -> None:
    """Run the quiz generation function in the background."""
    global is_blinking
    try:
        start_over()
        main(test_type_var.get(), push=line_push_var.get(),
             questions=int(questions_var.get()))
        # Update the status_label's text to show success
        status_label.configure(text="クイズの作成が完了しました！")
        # Automatically update the Text widget after quiz generation
        load_file(NEWS_ARTICLE_LOCATION)
        send_button.configure(state="normal")  # Enable the send button
        # Enable the file load buttons
        load_article_button.configure(state="normal")
        load_def_quiz_button.configure(state="normal")
        load_pron_quiz_button.configure(state="normal")
        load_log_button.configure(state="normal")
        # Reset the status_label's text to an empty string after 5 seconds
        root.after(5000, lambda: status_label.configure(text=""))
        is_blinking = False
        if line_push_var.get():
            messagebox.showinfo("成功", "クイズがLINEに送信されました！")
    except ValueError:
        messagebox.showerror("エラー", "最大問題数を指定してください。")
        is_blinking = False
        status_label.config(text="")
    except PermissionError as e:
        messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")
        is_blinking = False
        status_label.config(text="")
    except ConnectionError as e:
        messagebox.showerror("エラー", f"クイズの発信に失敗しました: {e}")
        is_blinking = False
        status_label.config(text="")


def increment_questions() -> None:
    """Increase the value of the questions Entry."""
    current_value_str = questions_var.get().strip()
    if not current_value_str.isdigit():
        questions_var.set("1")
    else:
        current_value = int(current_value_str)
        questions_var.set(str(current_value + 1))


def decrement_questions() -> None:
    """Decrease the value of the questions Entry."""
    current_value_str = questions_var.get().strip()
    if not current_value_str.isdigit():
        questions_var.set("1")
    else:
        current_value = int(current_value_str)
        if current_value > 1:
            questions_var.set(str(current_value - 1))


def press_push_quiz_button() -> None:
    """Send the quiz to LINE."""
    try:
        if test_type_var.get() == "読み方クイズ":
            push_quiz(PRONOUN_QUIZ_LOCATION)
        else:
            push_quiz(DEF_QUIZ_LOCATION)
        messagebox.showinfo("成功", "クイズを発信しました！")
        with open(LOG_LOCATION, 'a', encoding='utf-8') as f:
            f.write('PUSHED\n')
    except PermissionError as e:
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
        return None
    current_text = status_label.cget("text")
    if current_text == "クイズの作成が完了しました！":
        return None
    if current_text == "何も押さないでください。クイズ作成中":
        new_text = "何も押さないでください。クイズ作成中・"
    elif current_text == "何も押さないでください。クイズ作成中・":
        new_text = "何も押さないでください。クイズ作成中・・"
    elif current_text == "何も押さないでください。クイズ作成中・・":
        new_text = "何も押さないでください。クイズ作成中・・・"
    else:
        new_text = "何も押さないでください。クイズ作成中"

    status_label.configure(text=new_text)
    root.after(750, update_status_label_blink)  # Schedule the next update


# Create the main window
root = ctk.CTk()
root.title(f'NHK NEWS EASY クイズ作成 GUI {VERSION}')
root.geometry("900x556")
root.configure(font="Mincho", size="15")
root.iconbitmap(NHK_ICON_LOCATION)

ctk.set_appearance_mode("dark")

tab_view = ctk.CTkTabview(root)
tab_view.add("1")
tab_view.add("2")
tab_view_label = ctk.CTkLabel(master=tab_view.tab("1"))
tab_view_label.grid(row=2, column=2, padx=20, pady=10)

# Padding for the labels and the entry widgets
entry_padding = 6

# Padding for the buttons
button_padding = 10

# Create the widgets
status_label = ctk.CTkLabel(root, text="")
status_label.grid(row=3, column=1, padx=(230, 0), sticky="w")

# Create the test type radio buttons
test_type_var = ctk.StringVar()
line_push_var = ctk.BooleanVar()
questions_var = ctk.StringVar()

# Create a menu bar
menu_bar = tk.Menu(root)
root.configure(menu=menu_bar)

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

# Create the test type label and combobox
test_type_label = ctk.CTkLabel(root, text="クイズタイプ:")
test_type_label.grid(row=0, column=0, padx=entry_padding,
                     pady=entry_padding, sticky="w")
test_type_combobox = ctk.CTkComboBox(root, variable=test_type_var, values=[
    "読み方クイズ", "単語意味クイズ"], state="readonly")
test_type_combobox.grid(row=0, column=1, padx=entry_padding,
                        pady=entry_padding, sticky="w")

# Create the line push label and checkbutton
line_push_label = ctk.CTkLabel(root, text="すぐLINEに発信:")
line_push_label.grid(row=1, column=0, padx=entry_padding,
                     pady=entry_padding, sticky="w")
line_push_check = ctk.CTkCheckBox(root, variable=line_push_var, text="")
line_push_check.grid(row=1, column=1, padx=entry_padding,
                     pady=entry_padding, sticky="w")

# Create the questions label and entry
questions_label = ctk.CTkLabel(root, text="最大問題数:")
questions_label.grid(row=2, column=0, padx=entry_padding,
                     pady=entry_padding, sticky="w")
questions_entry = ctk.CTkEntry(root, textvariable=questions_var, width=30)
questions_entry.insert(0, DEFAULT_NUMBER_OF_QUESTIONS)
questions_entry.grid(row=2, column=1, padx=entry_padding,
                     pady=entry_padding, sticky="w")

# Create the increment and decrement buttons
increment_button = ctk.CTkButton(
    root, text="▲", command=increment_questions, width=30)
increment_button.grid(row=2, column=1, padx=(35, 0), pady=(0, 0), sticky="w")
decrement_button = ctk.CTkButton(
    root, text="▼", command=decrement_questions, width=30)
decrement_button.grid(row=2, column=1, padx=(80, 0), pady=(0, 0), sticky="w")

# Create the generate and send buttons
generate_button = ctk.CTkButton(
    root, text="クイズ作成", command=start_quiz_generation_thread)
generate_button.grid(row=3, column=1, padx=button_padding,
                     pady=button_padding, sticky="w")
send_button = ctk.CTkButton(
    root, text="LINEに発信", command=press_push_quiz_button, state="disabled")
send_button.grid(row=3, column=1, padx=(
    110 + button_padding, 0), pady=button_padding, sticky="w")

# Create the article label and text widget
article_label = ctk.CTkLabel(root, text="ファイル表示:")
article_label.grid(row=4, column=0, sticky="w")
article_text = ctk.CTkTextbox(root, wrap=tk.WORD, width=45, height=28)
article_text.grid(row=5, column=0, columnspan=2,
                  padx=10, pady=10, sticky="nsew")

# Create a scrollbar for the article text widget
scrollbar = ctk.CTkScrollbar(root, command=article_text.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
article_text.configure(yscrollcommand=scrollbar.set)

# Create the load file buttons
load_article_button = ctk.CTkButton(
    root, text="ニュース文章", command=lambda: load_file(NEWS_ARTICLE_LOCATION), state="disabled")
load_article_button.grid(row=4, column=1, sticky="w")

load_def_quiz_button = ctk.CTkButton(
    root, text="単語意味クイズ", command=lambda: load_file(DEF_QUIZ_LOCATION), state="disabled")
load_def_quiz_button.grid(row=4, column=1, padx=(125, 0), sticky="w")

load_pron_quiz_button = ctk.CTkButton(
    root, text="読み方クイズ", command=lambda: load_file(PRONOUN_QUIZ_LOCATION), state="disabled")
load_pron_quiz_button.grid(row=4, column=1, padx=(265, 0), sticky="w")

load_log_button = ctk.CTkButton(
    root, text="ログファイル", command=lambda: load_file(LOG_LOCATION))
load_log_button.grid(row=4, column=1, padx=(390, 0), sticky="w")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(5, weight=1)

root.mainloop()
