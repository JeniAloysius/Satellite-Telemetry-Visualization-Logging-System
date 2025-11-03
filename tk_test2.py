import tkinter as tk
from tkinter import messagebox

def say_hello():
    messagebox.showinfo("Tk Test", "✅ Tkinter Messagebox Active!\nUnicode: ☕🚀✨")

root = tk.Tk()
root.title("Tkinter Test 2")

label = tk.Label(root, text="Testing messagebox + emoji support ☕")
label.pack(pady=10)

test_button = tk.Button(root, text="Show Message", command=say_hello)
test_button.pack(pady=5)

quit_button = tk.Button(root, text="QUIT", command=root.destroy)
quit_button.pack(pady=5)

root.mainloop()
