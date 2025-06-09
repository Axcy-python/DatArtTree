import customtkinter as ctk
from PIL import Image


class LoadScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.__settings()
        self.__center_win()
        self.show()

    def show(self):
        # Тут можна буде вставити анімацію, зображення і т.п.
        label = ctk.CTkLabel(self, text="Завантаження DatArtTree...", font=ctk.CTkFont(size=20))
        label.pack(pady=150)

    def __settings(self):
        self.title("DatArtTree")
        self.overrideredirect(True)  # Без рамки
        self.geometry("600x400")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        print("Програму закрито!")
        self.destroy()

    def __center_win(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        pos_x = (self.winfo_screenwidth() - width) // 2
        pos_y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
