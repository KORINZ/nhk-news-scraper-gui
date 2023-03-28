import tkinter as tk
from tkinter import messagebox
from main import main


def run_quiz_generation():
    try:
        main(test_type_var.get(), push=line_push_var.get(),
             questions=int(questions_var.get()))
        messagebox.showinfo("Success", "Quiz generation completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


root = tk.Tk()
root.title("NHK Easy Quiz Generator")

test_type_var = tk.StringVar()
line_push_var = tk.BooleanVar()
questions_var = tk.StringVar()

test_type_label = tk.Label(root, text="Test Type:")
test_type_label.grid(row=0, column=0, sticky="w")
test_type_option = tk.OptionMenu(
    root, test_type_var, "PRONOUN_QUIZ_LOCATION", "DEF_QUIZ_LOCATION")
test_type_option.grid(row=0, column=1, sticky="w")

line_push_label = tk.Label(root, text="Push to LINE:")
line_push_label.grid(row=1, column=0, sticky="w")
line_push_check = tk.Checkbutton(root, variable=line_push_var)
line_push_check.grid(row=1, column=1, sticky="w")

questions_label = tk.Label(root, text="Number of Questions:")
questions_label.grid(row=2, column=0, sticky="w")
questions_entry = tk.Entry(root, textvariable=questions_var)
questions_entry.grid(row=2, column=1, sticky="w")

generate_button = tk.Button(
    root, text="Generate Quiz", command=run_quiz_generation)
generate_button.grid(row=3, columnspan=2)

root.mainloop()
