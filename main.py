import sys
import os
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QCompleter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = os.getenv("OPENWEATHER_API_KEY", "113546946d0b69cd77d2f32be0b139ea")

        self.city_label = QLabel("Enter City Name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.get_location_button = QPushButton("Get My Location Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)

        self.previous_searches = ["New York", "Los Angeles", "London", "Tokyo", "Delhi", "Sydney"]
        self.completer = QCompleter(self.previous_searches)
        self.city_input.setCompleter(self.completer)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather Anytime")
        self.setWindowIcon(QIcon("weather_icon.png"))
        self.setFixedSize(500, 600)

        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        self.city_input.setFixedHeight(50)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.get_location_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")

        self.city_label.setText("<span style='font-size: 40px; font-weight: bold;'>Enter City Name:</span>")
        self.city_label.setTextFormat(Qt.RichText)

        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: white;
            }
            QLabel {
                font-family: Arial;
            }
            QLabel#city_label {
                font-size: 35px;
                color: #D8DEE9;
            }
            QLineEdit {
                font-size: 25px;
                border: 2px solid #81A1C1;
                border-radius: 5px;
                padding: 5px;
                background-color: #3B4252;
                color: white;
            }
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #81A1C1;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #88C0D0;
            }
            QLabel#temperature_label {
                font-size: 75px;
            }
            QLabel#emoji_label {
                font-size: 60px;
                font-family: Apple Color Emoji;
            }
            QLabel#description_label {
                font-size: 20px;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)
        self.get_location_button.clicked.connect(self.get_current_location_weather)

    def get_weather(self):
        city = self.city_input.text().strip()

        if not city:
            self.display_error("Please enter a city name")
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") == 200:
                self.display_weather(data)
            else:
                self.display_error(f"Error: {data.get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            self.display_error(f"Request error: {e}")

    def get_current_location_weather(self):
        try:
            ip_info = requests.get("https://ipinfo.io/").json()
            lat, lon = ip_info["loc"].split(",")
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.api_key}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") == 200:
                self.display_weather(data)
            else:
                self.display_error(f"Error: {data.get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            self.display_error("Could not fetch location-based weather.")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px; color: red;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_c = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        city_name = data.get("name", "Unknown City")

        emoji = self.get_weather_emoji(weather_id)

        self.city_label.setText(f"<span style='font-size: 50px; font-weight: bold;'>{city_name}</span>")
        self.temperature_label.setText(f"{temperature_c:.0f}°C")

        self.emoji_label.setText(f"<span style='font-size: 100px; font-family: \"Noto Color Emoji\", \"Apple Color Emoji\";'>{emoji}</span>")
        self.emoji_label.setTextFormat(Qt.RichText)

        self.description_label.setText(
            f"{weather_description.capitalize()}\n"
            f"Humidity: {humidity}%\n"
            f"Wind: {wind_speed} m/s\n"
            f"Feels Like: {feels_like:.1f}°C"
        )

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌩️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())







