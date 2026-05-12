import tkinter as tk
from src.app_ui import AppUI

def main():
    root = tk.Tk()
    app = AppUI(root)

    root.update_idletasks()
    root.update()

    root.mainloop()

if __name__ == "__main__":
    main()