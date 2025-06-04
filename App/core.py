import customtkinter as ctk
from PIL import Image

class AppCore(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.__settings()
        self.__center_win()
        self.show()


    def show(self):
        bg_loadscreen: ctk.CTkImage = ctk.CTkImage()

    
    def __settings(self):
        self.title(f"DatArtTree")
        self.overrideredirect(True)
        self.geometry("600x400")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def on_close(self):
        print("Програму закрито!")
        self.destroy()

    
    def __center_win(self):
        self.update_idletasks()
        width: int = self.winfo_width()
        height: int = self.winfo_height()

        pos_x: int = (self.winfo_screenwidth() - width) // 2
        pos_y: int = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


if __name__ == "__main__":
    app = AppCore()
    app.mainloop()
