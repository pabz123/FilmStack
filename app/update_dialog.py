import tkinter as tk
from tkinter import messagebox

class UpdateDialog:
    def __init__(self, master):
        self.master = master
        master.title("Update Notification")
        master.geometry("300x150")
        master.config(bg="#f0f0f0")

        self.label = tk.Label(master, text="An update is available!", bg="#f0f0f0", font=("Helvetica", 14))
        self.label.pack(pady=20)

        self.ok_button = tk.Button(master, text="OK", command=master.quit, bg="#4CAF50", fg="white")
        self.ok_button.pack(pady=10)

def main():
    root = tk.Tk()
    dialog = UpdateDialog(root)
    root.mainloop()

if __name__ == "__main__":
    main()