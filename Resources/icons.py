import os
from customtkinter import CTkImage
from PIL import Image

ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons')

# Словник для зберігання зображень
_icons = {}

# Завантажуємо всі .png файли з папки icons
for filename in os.listdir(ICON_PATH):
    if filename.endswith('.png'):
        name = os.path.splitext(filename)[0]
        path = os.path.join(ICON_PATH, filename)

        # Завантаження і створення CTkImage
        image = CTkImage(light_image=Image.open(path), size=(24, 24))
        _icons[name] = image

# Робимо доступні змінні для імпорту
globals().update(_icons)