import unittest
import pandas as pd
from typing import Literal

# Дані
data = [
    {"Країна": "Україна", "Місто": "Київ", "Температура (°C)": 22, "Вологість (%)": 60, "Стан": "Сонячно"},
    {"Країна": "Україна", "Місто": "Київ", "Температура (°C)": 30, "Вологість (%)": 60, "Стан": "Сонячно"},
    {"Країна": "Україна", "Місто": "Київ", "Температура (°C)": 11, "Вологість (%)": 60, "Стан": "Сонячно"},
    {"Країна": "Україна", "Місто": "Київ", "Температура (°C)": 11, "Вологість (%)": 60, "Стан": "Сонячно"},
    {"Країна": "Україна", "Місто": "Київ", "Температура (°C)": 15, "Вологість (%)": 60, "Стан": "Сонячно"},
    {"Країна": "Польща", "Місто": "Варшава", "Температура (°C)": 18, "Вологість (%)": 70, "Стан": "Хмарно"},
    {"Країна": "Німеччина", "Місто": "Берлін", "Температура (°C)": 20, "Вологість (%)": 65, "Стан": "Дощ"},
    {"Країна": "Франція", "Місто": "Париж", "Температура (°C)": 24, "Вологість (%)": 55, "Стан": "Сонячно"},
    {"Країна": "Італія", "Місто": "Рим", "Температура (°C)": 28, "Вологість (%)": 50, "Стан": "Сонячно"},
    {"Країна": "Іспанія", "Місто": "Мадрид", "Температура (°C)": 30, "Вологість (%)": 40, "Стан": "Сонячно"},
    {"Країна": "Велика Британія", "Місто": "Лондон", "Температура (°C)": 17, "Вологість (%)": 80, "Стан": "Хмарно"},
    {"Країна": "Норвегія", "Місто": "Осло", "Температура (°C)": 12, "Вологість (%)": 75, "Стан": "Дощ"},
    {"Країна": "Швеція", "Місто": "Стокгольм", "Температура (°C)": 14, "Вологість (%)": 78, "Стан": "Хмарно"},
    {"Країна": "Фінляндія", "Місто": "Гельсінкі", "Температура (°C)": 10, "Вологість (%)": 85, "Стан": "Дощ"}
]
df = pd.DataFrame(data)

# Імпортуємо тестований клас
from backend import DataAnalizer

class TestDataAnalizer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DataAnalizer(df)

    def test_autopct_percent(self):
        func = self.analyzer.autopct('percent', [])
        self.assertEqual(func(25.5), '25.5%')

    def test_autopct_value(self):
        values = [10, 20, 30]
        func = self.analyzer.autopct('value', values)
        self.assertEqual(func(50), '30.0')  # 50% of sum([10+20+30]) = 30

    def test_autopct_combined(self):
        values = [10, 20, 30]
        func = self.analyzer.autopct('combined', values)
        self.assertEqual(func(50), '30.0 (50.0%)')

    def test_autopct_invalid(self):
        with self.assertRaises(ValueError):
            self.analyzer.autopct('invalid_mode', [1, 2, 3])

    def test_agregation_mean(self):
        result = self.analyzer.agregation('Країна', 'Температура (°C)', df, 'mean')
        self.assertIsInstance(result, pd.Series)

    def test_agregation_sum(self):
        result = self.analyzer.agregation('Країна', 'Температура (°C)', df, 'sum')
        self.assertTrue(result.sum() == df['Температура (°C)'].sum())

    def test_agregation_max(self):
        result = self.analyzer.agregation('Країна', 'Температура (°C)', df, 'max')
        self.assertEqual(result.max(), df['Температура (°C)'].max())

    def test_agregation_min(self):
        result = self.analyzer.agregation('Країна', 'Температура (°C)', df, 'min')
        self.assertEqual(result.min(), df['Температура (°C)'].min())

    def test_agregation_median(self):
        result = self.analyzer.agregation('Країна', 'Температура (°C)', df, 'median')
        self.assertIsInstance(result, pd.Series)

    def test_agregation_invalid(self):
        with self.assertRaises(ValueError):
            self.analyzer.agregation('Країна', 'Температура (°C)', df, 'unsupported')

if __name__ == '__main__':
    unittest.main()
