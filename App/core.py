import customtkinter as ctk
import time
from PIL import Image, ImageTk


class AnimatedApp:
    def __init__(self, root):
        self.root: ctk.CTk = root
        self.root.title("Delta Time Animation")

        img = Image.open("/Users/axcy/Desktop/PythonProjects/DatArtTree CTkinter App/Resources/icons/hello.png")
        img = img.convert("RGBA")

        # Перетворення в зображення Tkinter
        self.tk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))

        # Створення кнопки
        self.button = ctk.CTkButton(self.root, text="Animate Me", command=self.start_animation, image=self.tk_image)
        self.button.pack(pady=20)

        # Параметри анімації
        self.x = 50  # Початкове положення
        self.speed = 50  # Пікселі на секунду
        self.last_time = time.time()  # Зберігаємо час останнього кадру

        # Флаг, чи анімація повинна йти
        self.animating = False

    def start_animation(self):
        """Запускає анімацію"""
        self.animating = True
        self.last_time = time.time()  # Оновлюємо час старту анімації
        self.animate()

    def animate(self):
        """Анімація з дельта-часом"""
        if self.animating:
            # Поточний час
            current_time = time.time()

            # Різниця між поточним часом і часом останнього кадру
            delta_time = current_time - self.last_time

            # Оновлення положення об'єкта за допомогою delta_time
            self.x += self.speed * delta_time  # Множимо швидкість на час, щоб компенсувати FPS

            # Оновлюємо позицію кнопки
            self.button.place(x=self.x, y=100)

            # Оновлюємо час останнього кадру
            self.last_time = current_time

            # Якщо кнопка вийшла за межі екрану, зупиняємо анімацію
            if self.x > self.root.winfo_width():
                self.animating = False

            # Повторюємо анімацію через короткий інтервал
            self.root.after(1, self.animate)  # 16 мс = 60 FPS

if __name__ == "__main__":
    root = ctk.CTk()
    app = AnimatedApp(root)
    root.mainloop()
