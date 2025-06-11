import tkinter as tk
#from src.gui.gui import launch_app
from test_dir.test_camera import AccessControlApp  

if __name__ == "__main__":
    root = tk.Tk()
    app = AccessControlApp(root)
    root.mainloop()
    
    #launch_app() #decomment for other app
    

