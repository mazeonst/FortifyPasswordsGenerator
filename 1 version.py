import sys
import random
import string
import pyperclip
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox, QScrollArea, QDialog, QTextEdit, QInputDialog
from PyQt5.QtCore import Qt

def generate_password(length, use_numbers=False, use_special_chars=False):
    characters = string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_special_chars:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

class PasswordDialog(QDialog):
    def __init__(self, password_data):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Пароль и данные")
        self.setStyleSheet("background-color: #1a1a1a; color: #FFFFFF;")

        self.password_data = password_data

        self.password_label = QLabel(f"Пароль: {self.password_data['password']}")
        layout.addWidget(self.password_label)

        self.email_label = QLabel(f"Почта: {self.password_data['email']}")
        layout.addWidget(self.email_label)

        self.login_label = QLabel(f"Логин: {self.password_data['login']}")
        layout.addWidget(self.login_label)

        self.service_label = QLabel(f"Сервис: {self.password_data['service']}")
        layout.addWidget(self.service_label)

        copy_button = QPushButton("Скопировать")
        layout.addWidget(copy_button)
        copy_button.setStyleSheet("background-color: #007fff; color: #FFFFFF;")
        copy_button.clicked.connect(self.copy_password)

        save_button = QPushButton("Сохранить")
        layout.addWidget(save_button)
        save_button.setStyleSheet("background-color: #007fff; color: #FFFFFF;")
        save_button.clicked.connect(self.save_password)

        self.setLayout(layout)

    def copy_password(self):
        password = self.password_label.text().split(": ")[1]
        pyperclip.copy(password)
        print(f"Пароль скопирован в буфер обмена: {password}")

    def save_password(self):
        # Позволяет пользователю ввести имя сервиса
        service_name, ok = QInputDialog.getText(self, "Сохранить пароль", "Введите имя сервиса:")

        if ok:
            self.password_data["service"] = service_name
            # Здесь можно реализовать сохранение данных пароля и сервиса, например, в файл или базу данных.
            print(f"Пароль для сервиса {service_name} сохранен.")

class PasswordSaveDialog(QDialog):
    def __init__(self, passwords_and_data):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Сохраненные пароли и данные")
        self.setStyleSheet("background-color: #0e1621; color: #FFFFFF;")

        self.passwords_and_data = passwords_and_data
        password_text = ""

        for password_data in self.passwords_and_data:
            password_text += f"Сервис: {password_data['service']}\n"
            password_text += f"Пароль: {password_data['password']}\n"
            password_text += f"Почта: {password_data['email']}\n"
            password_text += f"Логин: {password_data['login']}\n\n"

        password_label = QTextEdit(self)
        password_label.setPlainText(password_text)
        layout.addWidget(password_label)

        self.setLayout(layout)

class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.num_passwords = 0
        self.length = 8
        self.use_numbers = False
        self.use_special_chars = False
        self.passwords_and_data = []

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: #0e1621;")

        num_passwords_label = QLabel("Сколько паролей сгенерировать:")
        self.num_passwords_input = QLineEdit(self)
        layout.addWidget(num_passwords_label)
        layout.addWidget(self.num_passwords_input)

        length_label = QLabel("Введите длину пароля:")
        self.length_input = QLineEdit(self)
        layout.addWidget(length_label)
        layout.addWidget(self.length_input)

        self.numbers_checkbox = QCheckBox("Включать цифры в парароль?")
        layout.addWidget(self.numbers_checkbox)

        self.special_chars_checkbox = QCheckBox("Включать специальные символы в парароль?")
        layout.addWidget(self.special_chars_checkbox)

        generate_button = QPushButton("Сгенерировать пароли")
        layout.addWidget(generate_button)
        generate_button.setStyleSheet("background-color: #007fff; color: #FFFFFF;")
        generate_button.clicked.connect(self.generate_passwords)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.scroll_area)

        self.password_display = QWidget()
        self.password_layout = QVBoxLayout(self.password_display)
        self.scroll_area.setWidget(self.password_display)

        # Кнопка "Сохранить пароли и данные"
        save_button = QPushButton("Сохранить пароли и данные")
        save_button.clicked.connect(self.save_passwords)
        layout.addWidget(save_button)
        save_button.setStyleSheet("background-color: #007fff; color: #FFFFFF;")

        self.setLayout(layout)
        self.setWindowTitle("Генератор паролей")
        self.setFixedSize(390, 844)
        self.show()

    def generate_passwords(self):
        self.num_passwords = int(self.num_passwords_input.text())
        self.length = int(self.length_input.text())
        self.use_numbers = self.numbers_checkbox.isChecked()
        self.use_special_chars = self.special_chars_checkbox.isChecked()

        # Очистить предыдущие пароли
        self.passwords_and_data.clear()
        for i in reversed(range(self.password_layout.count())):
            widget = self.password_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for _ in range(self.num_passwords):
            password = generate_password(self.length, self.use_numbers, self.use_special_chars)
            email = ""
            login = ""
            service = ""
            self.passwords_and_data.append({"password": password, "email": email, "login": login, "service": service})

        self.display_passwords()

    def open_password_dialog(self, password_data):
        dialog = PasswordDialog(password_data)
        dialog.exec()

    def display_passwords(self):
        for i, password_data in enumerate(self.passwords_and_data):
            password_label = QLabel(f"Пароль: {password_data['password']}")
            view_button = QPushButton("Посмотреть")
            view_button.clicked.connect(lambda _, password_data=password_data: self.open_password_dialog(password_data))
            self.password_layout.addWidget(password_label)
            self.password_layout.addWidget(view_button)

    def save_passwords(self):
        save_dialog = PasswordSaveDialog(self.passwords_and_data)
        save_dialog.exec()

        # Сохранить пароли в файл после закрытия диалога
        self.save_passwords_to_file()

    def save_passwords_to_file(self):
        # Создать или перезаписать файл с паролями
        with open("passwords.txt", "w") as file:
            for password_data in self.passwords_and_data:
                file.write(f"Сервис: {password_data['service']}\n")
                file.write(f"Пароль: {password_data['password']}\n")
                file.write(f"Почта: {password_data['email']}\n")
                file.write(f"Логин: {password_data['login']}\n")
                file.write("\n")

    def load_passwords_from_file(self):
        passwords_and_data = []
        try:
            with open("passwords.txt", "r") as file:
                lines = file.readlines()
                password_data = {}
                for line in lines:
                    line = line.strip()
                    if line.startswith("Сервис: "):
                        password_data["service"] = line[len("Сервис: "):]
                    elif line.startswith("Пароль: "):
                        password_data["password"] = line[len("Пароль: "):]
                    elif line.startswith("Почта: "):
                        password_data["email"] = line[len("Почта: "):]
                    elif line.startswith("Логин: "):
                        password_data["login"] = line[len("Логин: "):]
                    elif not line:
                        passwords_and_data.append(password_data)
                        password_data = {}
        except FileNotFoundError:
            pass
        return passwords_and_data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordGeneratorApp()

    # Загрузка ранее сохраненных паролей
    ex.passwords_and_data = ex.load_passwords_from_file()

    sys.exit(app.exec())
