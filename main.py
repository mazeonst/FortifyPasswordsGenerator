# Fortify
# Профессиональный генератор паролей, включающий в себя множество опций для генерации пароля
# GitHub: https://github.com/mazeonst/FortifyPasswordsGenerator
# Version:
# Developer: Michael Mirmikov
# Telegram: @mazeonst
# Email: mirmikovmisa@gmail.com

import sys
import random
import string
import pyperclip
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QScrollArea, QVBoxLayout, \
    QDialog, QTextEdit, QInputDialog, QMessageBox, QSplitter, QTextBrowser, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from cryptography.fernet import Fernet
from win10toast import ToastNotifier

# уведомления
toast = ToastNotifier()


# Функция для отправки уведомления
def send_notification(title, message):
    '''
    Функция для отправки уведомления через центр уведомлений Windows
    :param title: Заголовок уведомления
    :param message: Тело сообщения
    :param duration: Продолжительность видимости сообщения
    :param threaded: Этот параметр позволяет отображать уведомление справа
    '''

    toast.show_toast(
        title=title,
        msg=message,
        duration=5,
        threaded=True  # Этот параметр позволяет отображать уведомление справа
    )


def generate_password(length, use_numbers=False, use_special_chars=False, use_uppercase=True, use_lowercase=True,
                      user_word=""):
    '''
    Функция, которая генерирует случайный пароль указанной длины.
    :param length: Длинна пароля.
    :param use_numbers: Использовать буквы латинского алфавита?
    :param use_special_chars: Использовать специальные символы #$%&'()*+,-./:;<=>?@[\]^_`{|}~
    :param use_uppercase: Использовать символы верхнего регистра?
    :param use_lowercase: Использовать символы нижнего регистра?
    :param user_word: Добавить в начало пароля слово, введенное в ручную?
    '''

    characters = ''
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_special_chars:
        characters += string.punctuation
    if user_word:
        password = user_word + ''.join(random.choice(characters) for _ in range(length - len(user_word)))
    else:
        password = ''.join(random.choice(characters) for _ in range(length))

    return password


# PasswordDialog(QDialog): Диалоговое окно для отображения сгенерированного пароля и связанных с ним данных.
class PasswordDialog(QDialog):
    def __init__(self, password_data, encryption_key):
        """
        Конструктор класса PasswordDialog.

        Parameters:
            password_data (dict): Словарь с данными пароля.
            encryption_key (str): Ключ шифрования для зашифровки пароля.
        """
        super().__init__()

        self.setFixedSize(200, 250)

        self.is_encrypted = False

        self.setWindowIcon(QIcon('icon.png'))

        layout = QVBoxLayout()
        self.setWindowTitle("Пароль и данные")
        self.setStyleSheet("""

                        background-color: #0e1621; 
                        color: #FFFFFF; 
                        font-weight: 900;

                    """)

        self.password_data = password_data

        self.password_label = QLabel(f"Пароль: {self.password_data['password']}")
        layout.addWidget(self.password_label)

        self.email_label = QLabel(f"Почта: {self.password_data['email']}")
        layout.addWidget(self.email_label)

        self.login_label = QLabel(f"Логин: {self.password_data['login']}")
        layout.addWidget(self.login_label)

        self.service_label = QLabel(f"Сервис: {self.password_data['service']}")
        layout.addWidget(self.service_label)

        # кнопка "скопировать" для копирования паролей
        copy_button = QPushButton("Скопировать")
        copy_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 3px 1px; 
                                    font-size: 16px; 
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        copy_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        copy_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        copy_button.setStyleSheet(copy_button_style_released)
        copy_button.pressed.connect(lambda: copy_button.setStyleSheet(copy_button_style_pressed))
        copy_button.released.connect(lambda: copy_button.setStyleSheet(copy_button_style_released))
        layout.addWidget(copy_button)
        copy_button.clicked.connect(self.copy_password)

        # кнопка "сохранить", для сохранения пароля в текстовый документ
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 3px 1px; 
                                    font-size: 16px; 
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        save_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        save_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        save_button.setStyleSheet(save_button_style_released)
        save_button.pressed.connect(lambda: save_button.setStyleSheet(save_button_style_pressed))
        save_button.released.connect(lambda: save_button.setStyleSheet(save_button_style_released))
        layout.addWidget(save_button)
        save_button.clicked.connect(self.save_password)

        self.encryption_key = encryption_key

        # кнопка "зашифровать" для шифрования пароля
        encrypt_button = QPushButton("Зашифровать")
        encrypt_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 3px 1px; 
                                    font-size: 16px; 
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        encrypt_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        encrypt_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        encrypt_button.setStyleSheet(encrypt_button_style_released)
        encrypt_button.pressed.connect(lambda: encrypt_button.setStyleSheet(encrypt_button_style_pressed))
        encrypt_button.released.connect(lambda: encrypt_button.setStyleSheet(encrypt_button_style_released))
        layout.addWidget(encrypt_button)
        encrypt_button.clicked.connect(self.encrypt_password)

        # кнопка для отображения ключа шифрования в интерфейсе программы
        show_key_button = QPushButton("Ключ шифрования")
        show_key_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 3px 1px; 
                                    font-size: 16px; 
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        show_key_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        show_key_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        show_key_button.setStyleSheet(show_key_button_style_released)
        show_key_button.pressed.connect(lambda: show_key_button.setStyleSheet(show_key_button_style_pressed))
        show_key_button.released.connect(lambda: show_key_button.setStyleSheet(show_key_button_style_released))
        layout.addWidget(show_key_button)
        show_key_button.clicked.connect(self.show_encryption_key)
        self.setLayout(layout)

    def show_encryption_key(self):
        """
        Метод для отображения окна с ключом шифрования.
        """
        key_display_dialog = KeyDisplayDialog(self.encryption_key)
        key_display_dialog.exec()

    def encrypt_password(self):
        """
        Метод для шифрования пароля и обновления данных.
        """
        # Проверка, был ли пароль уже зашифрован
        if self.is_encrypted:
            QMessageBox.warning(self, "Предупреждение", "Пароль уже зашифрован.")
            return

        password = self.password_data["password"]
        fernet = Fernet(self.encryption_key)
        encrypted_password = fernet.encrypt(password.encode()).decode()  # Декодирование в строку
        self.password_data["password"] = encrypted_password
        self.is_encrypted = True  # Установите флаг после успешного шифрования
        print("Пароль зашифрован и обновлен.")
        # Отправляем уведомление
        send_notification("Пароль зашифрован", "Пароль успешно зашифрован!")

    def copy_password(self):
        """
        Метод для копирования пароля в буфер обмена и отправки уведомления.
        """
        password = self.password_label.text().split(": ")[1]
        pyperclip.copy(password)
        print(f"Пароль скопирован в буфер обмена: {password}")

        # Отправляем уведомление
        send_notification("Скопировано", "Пароль успешно скопирован в буфер обмена!")

    # def save_password(self)Ж: позволяет пользователю ввести данные для сохранения пароля в текстовый документ
    def save_password(self):
        """
        Метод для сохранения пароля в текстовый документ и отправки уведомления.
        """
        # Позволяет пользователю ввести имя сервиса (открывается окно)
        service_name, ok = QInputDialog.getText(self, "Сохранить пароль", "Введите имя сервиса:")

        if ok:
            self.password_data["service"] = service_name
            print(f"Пароль для сервиса {service_name} сохранен.")

        login_name, ok = QInputDialog.getText(self, "Сохранить пароль", "Введите логин:")

        if ok:
            self.password_data["login"] = login_name
            print(f"Пароль для сервиса {login_name} сохранен.")

        email_name, ok = QInputDialog.getText(self, "Сохранить пароль", "Введите почту:")

        if ok:
            self.password_data["email"] = email_name
            print(f"Пароль для сервиса {email_name} сохранен.")
            # Отправляем уведомление
            send_notification("Данные сохранены", "Пароль успешно сохранён!")


# KeyDisplayDialog(QDialog): Диалоговое окно для отображения ключа шифрования
class KeyDisplayDialog(QDialog):
    def __init__(self, encryption_key):
        """
        Конструктор класса KeyDisplayDialog.

        Parameters:
            encryption_key (str): Ключ шифрования для отображения.
        """
        super().__init__()
        self.setWindowTitle("Ключ шифрования")
        self.setWindowIcon(QIcon('icon.png'))
        layout = QVBoxLayout()
        self.setStyleSheet("""

                        background-color: #0e1621; 
                        color: #FFFFFF; 
                        font-weight: 900;
                        border: none;

                    """)
        key_label = QLabel("Ваш ключ шифрования:")
        layout.addWidget(key_label)

        key_text_edit = QTextEdit(str(encryption_key))
        layout.addWidget(key_text_edit)

        self.setLayout(layout)


# PasswordSaveDialog(QDialog): Диалоговое окно для отображения сохраненных паролей и связанных с ними данных.
class PasswordSaveDialog(QDialog):
    def __init__(self, passwords_and_data):
        """
        Конструктор класса PasswordSaveDialog.

        Parameters:
            passwords_and_data (list): Список словарей с сохраненными паролями и связанными данными.
        """
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Сохраненные пароли и данные")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("""

                        background-color: #0e1621;
                        color: #FFFFFF; 
                        font-weight: 900;
                        border: none;

                    """)
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


# PasswordGeneratorApp(QWidget): Главное окно приложения, в котором пользователь может настроить и генерировать пароли.
class PasswordGeneratorApp(QWidget):
    """
        Конструктор класса PasswordGeneratorApp.

        Инициализирует основные переменные и создает главное окно приложения.

        Attributes:
        - num_passwords (int): Количество генерируемых паролей.
        - length (int): Длина генерируемых паролей.
        - use_numbers (bool): Флаг использования цифр в паролях.
        - use_special_chars (bool): Флаг использования специальных символов в паролях.
        - passwords_and_data (list): Список сгенерированных паролей и связанных данных.
        - passwords_generated (bool): Флаг, указывающий, были ли сгенерированы пароли.
        - encryption_key (str): Ключ шифрования для использования в Fernet.
        """

    def __init__(self):
        super().__init__()

        self.num_passwords = 0
        self.length = 8
        self.use_numbers = False
        self.use_special_chars = False
        self.passwords_and_data = []
        self.passwords_generated = False
        self.encryption_key = Fernet.generate_key()
        self.initUI()

    def open_decrypt_dialog(self):
        """
        Метод для открытия диалогового окна расшифровки.
        """
        dialog = DecryptDialog(self.encryption_key)
        dialog.exec()

    def save_encryption_key(self):
        """
        Метод для сохранения ключа шифрования в файл.
        """
        with open("encryption_key.key", "wb") as key_file:
            key_file.write(self.encryption_key)
        print("Ключ шифрования сохранен.")

    def load_encryption_key(self):
        """
        Метод для загрузки ключа шифрования из файла.
        Если файл не найден, создает новый ключ и сохраняет его.
        """
        try:
            with open("encryption_key.key", "rb") as key_file:
                self.encryption_key = key_file.read().decode()
            print("Ключ шифрования загружен.")
        except FileNotFoundError:
            self.save_encryption_key()

    def encrypt_password(self, password):
        """
        Метод для шифрования пароля.

        Parameters:
            password (str): Пароль для шифрования.

        Returns:
            bytes: Зашифрованный пароль в виде байтов.
        """
        fernet = Fernet(self.encryption_key)
        encrypted_password = fernet.encrypt(password.encode())
        return encrypted_password

    def decrypt_password(self, encrypted_password):
        """
        Метод для расшифровки пароля.

        Parameters:
            encrypted_password (bytes): Зашифрованный пароль в виде байтов.

        Returns:
            str: Расшифрованный пароль в виде строки.
        """
        fernet = Fernet(self.encryption_key)
        decrypted_password = fernet.decrypt(encrypted_password).decode()
        return decrypted_password

    # Основное окно приложения
    def initUI(self):

        left_layout = QVBoxLayout()

        self.setStyleSheet("""

                        background-color: #0e1621; 
                        color: #FFF; 
                        font-weight: 900;

                    """)

        # num_passwords_input: Поле для ввода количества генерируемых паролей
        num_passwords_label = QLabel("Сколько паролей сгенерировать:")
        self.num_passwords_input = QLineEdit(self)
        left_layout.addWidget(num_passwords_label)
        left_layout.addWidget(self.num_passwords_input)
        self.num_passwords_input.setStyleSheet("""

                                            text-decoration: none; 
                                            border: none; 
                                            padding: 2px 1px; 
                                            font-size: 14px; 
                                            background-color: #2b5378; 
                                            color: #fff; 
                                            border-radius: 5px; 
                                            cursor: pointer; 
                                            font-family: Calibri; 
                                            font-weight: 900; 
                                            border: 1px solid #507EA0

                                        """)

        # length_input: Поле для ввода длины пароля
        length_label = QLabel("Введите длину пароля:")
        self.length_input = QLineEdit(self)
        left_layout.addWidget(length_label)
        left_layout.addWidget(self.length_input)
        self.length_input.setStyleSheet("""

                                        text-decoration: none; 
                                        border: none; 
                                        padding: 2px 1px; 
                                        font-size: 14px; 
                                        background-color: #2b5378; 
                                        color: #fff; 
                                        border-radius: 5px; 
                                        cursor: pointer; 
                                        font-family: Calibri; 
                                        font-weight: 900; 
                                        border: 1px solid #507EA0;

                                    """)

        self.word_input = QLineEdit(self)
        left_layout.addWidget(QLabel("Введите слово:"))
        left_layout.addWidget(self.word_input)
        self.word_input.setStyleSheet(
            "text-decoration: none; border: none; padding: 2px 1px; font-size: 14px; background-color: #2b5378; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 1px solid #507EA0")

        # numbers_checkbox: Флажок для включения цифр в пароль
        self.numbers_checkbox = QCheckBox("Включать цифры в пароль?")
        left_layout.addWidget(self.numbers_checkbox)

        # special_chars_checkbox: Флажок для включения специальных символов в пароль
        self.special_chars_checkbox = QCheckBox("Включать специальные символы в пароль?")
        left_layout.addWidget(self.special_chars_checkbox)

        self.use_uppercase_checkbox = QCheckBox("Использовать символы верхнего регистра?")
        left_layout.addWidget(self.use_uppercase_checkbox)

        self.use_lowercase_checkbox = QCheckBox("Использовать символы нижнего регистра?")
        left_layout.addWidget(self.use_lowercase_checkbox)

        # generate_button: Кнопка для запуска генерации паролей
        generate_button = QPushButton("Сгенерировать пароли")
        left_layout.addWidget(generate_button)
        generate_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 5px 1px; 
                                    font-size: 16px;    
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    cursor: pointer; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        generate_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        generate_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        generate_button.setStyleSheet(generate_button_style_released)
        generate_button.pressed.connect(lambda: generate_button.setStyleSheet(generate_button_style_pressed))
        generate_button.released.connect(lambda: generate_button.setStyleSheet(generate_button_style_released))

        generate_button.clicked.connect(self.generate_passwords)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # разделитель между левой и правой частью
        splitter = QSplitter()
        splitter.addWidget(left_widget)

        # scroll_area: Область прокрутки для отображения сгенерированных паролей
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFixedWidth(400)

        scroll_area_style = """
                    QScrollArea {
                        background-color: #2b5378;  
                        border-radius: 10px;         
                    }
                    QScrollBar:vertical {
                        border: none;               
                        background: #2b5378;        
                        width: 10px;                
                        border-radius: 10px;
                    }
                    QScrollBar::handle:vertical {
                        background: #149dfb;        
                        border-radius: 5px;         
                    }
                    QScrollBar::add-line:vertical {
                        height: 0;
                    }
                    QScrollBar::sub-line:vertical {
                        height: 0;
                    }
                """
        self.scroll_area.setStyleSheet(scroll_area_style)

        # Создайте виджет для правой части и установите для него поле для вывода паролей
        self.password_display = QWidget()
        self.password_layout = QVBoxLayout(self.password_display)
        self.scroll_area.setWidget(self.password_display)

        # Добавьте левую и правую части в разделитель
        splitter.addWidget(self.scroll_area)

        # основный макет для приложения
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        # Кнопка "Сохранить пароли и данные"
        save_button = QPushButton("Сгенерированные пароли")
        save_button.setStyleSheet("""

                                text-decoration: none; 
                                border: none; 
                                padding: 5px 1px; 
                                font-size: 16px; 
                                background-color: #149dfb; 
                                color: #fff; 
                                border-radius: 5px; 
                                cursor: pointer; 
                                font-family: Calibri; 
                                font-weight: 900; 
                                border: 2px solid #507EA0

                            """)
        # Анимация нажатия кнопки
        save_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        save_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        save_button.setStyleSheet(save_button_style_released)
        save_button.pressed.connect(lambda: save_button.setStyleSheet(save_button_style_pressed))
        save_button.released.connect(lambda: save_button.setStyleSheet(save_button_style_released))
        save_button.clicked.connect(self.save_passwords)
        left_layout.addWidget(save_button)

        decrypt_button = QPushButton("Расшифровать")
        left_layout.addWidget(decrypt_button)
        decrypt_button.setStyleSheet("""

                                    text-decoration: none; 
                                    border: none; 
                                    padding: 5px 1px; 
                                    font-size: 16px; 
                                    background-color: #149dfb; 
                                    color: #fff; 
                                    border-radius: 5px; 
                                    cursor: pointer; 
                                    font-family: Calibri; 
                                    font-weight: 900; 
                                    border: 2px solid #507EA0

                                """)
        # Анимация нажатия кнопки
        decrypt_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        decrypt_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        decrypt_button.setStyleSheet(decrypt_button_style_released)
        decrypt_button.pressed.connect(lambda: decrypt_button.setStyleSheet(decrypt_button_style_pressed))
        decrypt_button.released.connect(lambda: decrypt_button.setStyleSheet(decrypt_button_style_released))
        decrypt_button.clicked.connect(self.open_decrypt_dialog)

        buttons_container = QHBoxLayout()

        # Кнопка отвечающая за вопросы
        questions_button = QPushButton("Возможности")
        questions_button.setStyleSheet("""
            text-decoration: none; 
                                                    border: none; 
                                                    padding: 5px 1px; 
                                                    font-size: 16px; 
                                                    background-color: #0070FF; 
                                                    color: #fff; 
                                                    border-radius: 5px; 
                                                    cursor: pointer; 
                                                    font-family: Calibri; 
                                                    font-weight: 900; 
                                                    border: 2px solid #005CD2
        """)
        questions_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2; background-color: #74C5FF;"
        questions_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2;"
        questions_button.pressed.connect(lambda: questions_button.setStyleSheet(questions_button_style_pressed))
        questions_button.released.connect(lambda: questions_button.setStyleSheet(questions_button_style_released))
        questions_button.clicked.connect(self.show_fortify_pass_info)

        # Кнопка отвечающая за советы
        tips_button = QPushButton("Советы")
        tips_button.setStyleSheet("""
            text-decoration: none; 
                                                    border: none; 
                                                    padding: 5px 1px; 
                                                    font-size: 16px; 
                                                    background-color: #0070FF; 
                                                    color: #fff; 
                                                    border-radius: 5px; 
                                                    cursor: pointer; 
                                                    font-family: Calibri; 
                                                    font-weight: 900; 
                                                    border: 2px solid #005CD2
        """)
        tips_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2; background-color: #74C5FF;"
        tips_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2;"
        tips_button.pressed.connect(lambda: tips_button.setStyleSheet(tips_button_style_pressed))
        tips_button.released.connect(lambda: tips_button.setStyleSheet(tips_button_style_released))
        tips_button.clicked.connect(self.show_tips_window)

        # Добавление кнопок в контейнер
        buttons_container.addWidget(questions_button)
        buttons_container.addWidget(tips_button)

        # Добавление контейнера с кнопками в левый layout
        left_layout.addLayout(buttons_container)

        self.setLayout(left_layout)
        self.setWindowTitle("fortify")
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(780, 440)
        self.show()

    def show_tips_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Советы по генерации пароля")
        self.setWindowIcon(QIcon('icon.png'))
        dialog.setFixedSize(500, 400)

        dialog.setStyleSheet("background-color: #0e1621; border: none")

        info_text = QTextBrowser(dialog)
        info_text.setOpenExternalLinks(True)

        # Используем HTML для форматирования текста
        info_text.setHtml("""
            <html>
            <head>
                <style>
                    h1 { font-size: 20px; color: #FFF; font-weight: bold; }
                    h2 { font-size: 16px; color: #FFF; font-weight: bold; }
                    p { font-size: 14px; color: #FFF;}
                    p1 { font-size: 14px; color: #1f91d5;}
                </style>
            </head>
            <body>
                <h1>Советы по <p1>генерации пароля</p1></h1>
                <h2>Общие принципы:</h2>
                <p>1. Длину не менее <p1>8</p1> символов.</p>
                <p>2. Различные типы символов, такие как буквы <p1>верхнего</p1> и <p1>нижнего</p1> регистра, цифры и специальные символы.</p>
                <p>3. Не должен содержать <p1>личную информацию</p1>, такую как: <p1>имя</p1>, <p1>дату рождения</p1> или <p1>номер телефона</p1>.</p>
                <p>4. Не должен быть <p1>очевидным</p1> или легко угадываемым, например, <p1>последовательностью чисел</p1> или <p1>букв</p1> на клавиатуре.</p>
                <p>5. Лучше использовать <p1>фразу</p1> или <p1>комбинацию слов</p1>, которые легко запоминаются, но сложны для взлома.</p>
                <p>6. <p1>Регулярно менять пароль</p1> и не использовать один и тот же пароль для разных аккаунтов.</p>
            </body>
            </html>
        """)

        info_text.setGeometry(10, 10, 480, 380)

        dialog.exec()

    # Возможности программы
    def show_fortify_pass_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Возможности Fortify Pass")
        self.setWindowIcon(QIcon('icon.png'))
        dialog.setFixedSize(700, 580)

        dialog.setStyleSheet("background-color: #0e1621; border: none")

        info_text = QTextBrowser(dialog)
        info_text.setOpenExternalLinks(True)
        info_text.setHtml("""<
                    <html>
                    <head>
                        <style>
                            h1 { font-size: 20px; color: #FFF; font-weight: bold; }
                            h2 { font-size: 14px; color: #FFF; font-weight: bold; }
                            h3 { font-size: 18px; color: #FF0000; font-weight: bold; }
                            p { font-size: 12px; }
                            h11 { font-size: 20px; color: #1f91d5; font-weight: bold; }
                            h22 { font-size: 14px; color: #1f91d5; font-weight: bold; }
                            p1 { font-size: 12px; color: #1f91d5;}
                            p2 { font-size: 12px; color: #FF0000;}
                        </style>
                    </head>
                    <body>
                        <h1>Возможности <h11>Fortify Pass</h11></h1>
                        <h2>1. Генерация сразу <h22>нескольких паролей.</h22></h2>
                        <h2>2. Генерация пароля <h22>заданной пользователем длины.</h22></h2>
                        <h2>3. Интеграция в пароль своих <h22>фраз, слов.</h22></h2>
                        <h2>4. Использование разных <h22>опций</h22> для генерации пароля, таких как:</h2>
                        <p>1. Добавление <p1>цифр</p1> в пароль.</p>
                        <p>2. Добавление <p1>специальных символов</p1> в пароль.</p>
                        <p>3. Возможность выбора генерации символов <p1>разного регистра</p1>.</p>
                        <h2>Так же <h22>"FortifyPass"</h22> умеет шифровать пароль, благодаря такой библиотеке, как <h22>"cryptography.fernet"</h22></h2>
                        <p>1. При запуске программы автоматически загружается ключ шифрования в файл <p1>"encryption_key.key"</p1></p>
                        <h3><b>ВНИМАНИЕ!
КЛЮЧ ШИФРОВАНИЯ ВАЖНО СОХРАНИТЬ В ОТДЕЛЬНЫЙ ИСТОЧНИК ИНАЧЕ ЕСТЬ ВЕРОЯТНОСТЬ ПОТЕРИ ВСЕХ ЗАШИФРОВАННЫХ ДАННЫХ!</b></h3>
                        <p>2. В окне <p1>"пароль и данные"</p1> есть кнопка <p1>"зашифровать"</p1> после нажатия которой, пароль шифруется и записывается в файл <p1>"passwords.txt"</p1>. 
                        <p>3. На главном экране программы имеется кнопка <p1>"Расшифровать"</p1> после ее нажатия открывается окно <p1>"Расшифровать пароль"</p1> в котором благодаря ранее сохраненному ключу шифрования вы можете расшифровать данные</p>
                        <p><center>©Michael Mirmikov</center></p>
                    </body>
                    </html>
                """)
        info_text.setGeometry(10, 10, 680, 560)

        dialog.exec()

    # generate_passwords(): Метод для генерации паролей на основе введенных настроек.
    def generate_passwords(self):
        """
        Метод для генерации паролей на основе введенных настроек.

        Пароли генерируются в соответствии с введенными параметрами пользователем:
        количество паролей, длина, использование цифр и специальных символов.

        Проверяет корректность введенных значений и устанавливает флаг passwords_generated.
        """

        if not self.num_passwords_input.text() or not self.length_input.text():
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, выберите все параметры перед генерацией паролей.")
            return

        # Получите значения параметров
        num_passwords_text = self.num_passwords_input.text()
        length_text = self.length_input.text()
        user_word = self.word_input.text()

        # Проверьте, что пользователь ввел числа для количества паролей и длины
        if not num_passwords_text.isdigit() or not length_text.isdigit():
            QMessageBox.critical(self, "Ошибка",
                                 "Пожалуйста, введите корректные значения для количества паролей и длины!")
            return

        if not num_passwords_text or not length_text:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, введите количество паролей и длину!")
            return

        self.num_passwords = int(num_passwords_text)
        self.length = int(length_text)
        self.use_numbers = self.numbers_checkbox.isChecked()
        self.use_special_chars = self.special_chars_checkbox.isChecked()
        self.use_uppercase = self.use_uppercase_checkbox.isChecked()
        self.use_lowercase = self.use_lowercase_checkbox.isChecked()
        self.passwords_generated = True

        if not self.use_numbers and not self.use_special_chars and not self.use_uppercase and not self.use_lowercase:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, установите хотя бы одну опцию для генерации паролей!")
            return

        # Очистить предыдущие пароли
        self.passwords_and_data.clear()
        for i in reversed(range(self.password_layout.count())):
            widget = self.password_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for _ in range(self.num_passwords):
            password = generate_password(self.length, self.use_numbers, self.use_special_chars, self.use_uppercase,
                                         self.use_lowercase, user_word)
            email = ""
            login = ""
            service = ""
            self.passwords_and_data.append({"password": password, "email": email, "login": login, "service": service})

        self.display_passwords()

    # open_password_dialog(password_data): Метод для открытия диалогового окна с сгенерированным паролем.
    def open_password_dialog(self, password_data):
        """
        Метод для открытия диалогового окна с сгенерированным паролем.

        Args:
        - password_data (dict): Словарь с данными о пароле.

        Открывает диалоговое окно с сгенерированным паролем и использует encryption_key для расшифровки.
        """
        dialog = PasswordDialog(password_data, self.encryption_key)
        dialog.exec()

    # display_passwords(): Метод для отображения сгенерированных паролей и кнопок "Посмотреть".
    def display_passwords(self):
        """
        Метод для отображения сгенерированных паролей и кнопок "Посмотреть".

        Создает виджеты для отображения паролей и кнопок "Посмотреть" в главном окне.
        """
        for i, password_data in enumerate(self.passwords_and_data):
            password_label = QLabel(f"Пароль: {password_data['password']}")
            view_button = QPushButton("Посмотреть")
            view_button.setStyleSheet("""
                                      text-decoration: none; 
                                      border: none; 
                                      padding: 3px 1px; 
                                      font-size: 16px; 
                                      background-color: #149dfb; 
                                      color: #fff; 
                                      border-radius: 5px; 
                                      font-family: Calibri; 
                                      font-weight: 900; 
                                      border: 2px solid #507EA0;
                                      """)
            view_button.clicked.connect(lambda _, password_data=password_data: self.open_password_dialog(password_data))
            self.password_layout.addWidget(password_label)
            self.password_layout.addWidget(view_button)

    # save_passwords(): Метод для открытия диалогового окна для сохранения паролей и данных.
    def save_passwords(self):
        """
        Метод для открытия диалогового окна сохранения паролей и данных.

        Проверяет, были ли сгенерированы пароли, и открывает соответствующее диалоговое окно.
        Сохраняет пароли в файл passwords.txt после закрытия диалогового окна.
        """
        # Check if passwords have been generated
        if not self.passwords_generated:
            QMessageBox.critical(self, "Ошибка", "Сначала сгенерируйте пароли!")
            return

        save_dialog = PasswordSaveDialog(self.passwords_and_data)
        save_dialog.exec()

        # Сохранить пароли в файл после закрытия диалога
        self.save_passwords_to_file()

    # save_passwords_to_file(): Метод для сохранения паролей и данных в файле.
    def save_passwords_to_file(self):
        """
        Метод для сохранения паролей и данных в файле.

        Создает или перезаписывает файл с паролями на основе данных из passwords_and_data.
        """
        # Создать или перезаписать файл с паролями
        with open("passwords.txt", "w") as file:
            for password_data in self.passwords_and_data:
                file.write(f"Сервис: {password_data['service']}\n")
                file.write(f"Пароль: {password_data['password']}\n")
                file.write(f"Почта: {password_data['email']}\n")
                file.write(f"Логин: {password_data['login']}\n")
                file.write("\n")

    # load_passwords_from_file(): Метод для загрузки ранее сохраненных паролей из файла.
    def load_passwords_from_file(self):
        """
        Метод для загрузки паролей и данных из файла.

        Возвращает список словарей с данными о паролях, прочитанными из файла passwords.txt.
        """
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


# DecryptDialog(QDialog): Класс для окна расшифровки пароля
class DecryptDialog(QDialog):
    def __init__(self, encryption_key):
        """
        Конструктор класса DecryptDialog.

        Инициализирует диалоговое окно для расшифровки пароля.

        Args:
        - encryption_key (str): Ключ шифрования в формате Fernet.
        """
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Расшифровать пароль")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("""
                           background-color: #0e1621; 
                           color: #FFFFFF; 
                           font-weight: 900;
                           """)

        self.encryption_key = encryption_key

        # Конвертируем ключ безопасности в строку и устанавливаем его в поле ввода
        self.encryption_key_str = encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key
        self.key_label = QLabel("Введите ключ безопасности:")
        layout.addWidget(self.key_label)

        self.key_input = QLineEdit(self)
        self.key_input.setText(self.encryption_key_str)
        layout.addWidget(self.key_input)
        self.key_input.setStyleSheet("""
                                     text-decoration: none; 
                                     border: none; 
                                     padding: 2px 1px; 
                                     font-size: 14px; 
                                     background-color: #2b5378; 
                                     color: #fff; 
                                     border-radius: 5px; 
                                     cursor: pointer; 
                                     font-family: Calibri; 
                                     font-weight: 900; 
                                     border: 1px solid #507EA0;
                                     """)

        self.encrypted_text_label = QLabel("Введите зашифрованный текст:")
        layout.addWidget(self.encrypted_text_label)

        self.encrypted_text_input = QLineEdit(self)
        layout.addWidget(self.encrypted_text_input)
        self.encrypted_text_input.setStyleSheet("""
                                                text-decoration: none; 
                                                border: none; 
                                                padding: 2px 1px; 
                                                font-size: 14px; 
                                                background-color: #2b5378; 
                                                color: #fff; 
                                                border-radius: 5px; 
                                                cursor: pointer; 
                                                font-family: Calibri; 
                                                font-weight: 900; 
                                                border: 1px solid #507EA0;
                                                """)

        decrypt_button = QPushButton("Расшифровать текст")
        layout.addWidget(decrypt_button)
        decrypt_button.setStyleSheet("""
                                     text-decoration: none; 
                                     border: none; 
                                     padding: 5px 1px; 
                                     font-size: 16px; 
                                     background-color: #149dfb; 
                                     color: #fff; 
                                     border-radius: 5px; 
                                     cursor: pointer; 
                                     font-family: Calibri; 
                                     font-weight: 900; 
                                     border: 2px solid #507EA0
                                    """)
        decrypt_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2; background-color: #74C5FF;"
        decrypt_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2;"
        decrypt_button.pressed.connect(lambda: decrypt_button.setStyleSheet(decrypt_button_style_pressed))
        decrypt_button.released.connect(lambda: decrypt_button.setStyleSheet(decrypt_button_style_released))
        decrypt_button.clicked.connect(self.decrypt_text)

        self.setLayout(layout)

    def decrypt_text(self):
        """
        Метод для расшифровки текста.

        Пытается расшифровать текст, используя введенный ключ и зашифрованный текст.
        Выводит результат в диалоговое окно.
        """
        key = self.key_input.text()
        encrypted_text = self.encrypted_text_input.text()
        try:
            fernet = Fernet(key.encode())
            decrypted_text = fernet.decrypt(encrypted_text.encode()).decode()
            QMessageBox.information(self, "Расшифрованный текст", f"Расшифрованный текст: {decrypted_text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 "Не удалось расшифровать текст. Убедитесь, что ключ и зашифрованный текст верны.")


# В if __name__ == '__main__': блоке приложение и главное окно ex создаются, и производится загрузка ранее сохраненных паролей из файла.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordGeneratorApp()

    # Загрузка ключа шифрования
    ex.load_encryption_key()

    # Загрузка ранее сохраненных паролей
    ex.passwords_and_data = ex.load_passwords_from_file()

    sys.exit(app.exec())
