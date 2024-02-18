# Fortify
# A professional password generator that includes many options for password generation
# GitHub: https://github.com/mazeonst/FortifyPasswordsGenerator
# Version: 1.2.8
# Developer: Michael Mirmikov
# Telegram: @mazeonst
# Email: mirmikovmisa@gmail.com
import sys
import random
import string
import pyperclip
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QScrollArea, QVBoxLayout, QDialog, QTextEdit, QInputDialog, QMessageBox, QSplitter, QTextBrowser, QHBoxLayout, QComboBox, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from cryptography.fernet import Fernet
from win10toast import ToastNotifier
import subprocess

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

        self.setFixedSize(170, 215)

        self.is_encrypted = False

        self.setWindowIcon(QIcon('icon.png'))

        layout = QVBoxLayout()
        self.setWindowTitle("Password and data")
        self.setStyleSheet("""

                        background-color: #0e1621; 
                        color: #FFFFFF; 
                        font-weight: 900;

                    """)

        self.password_data = password_data

        self.password_label = QLabel(f"Password: {self.password_data['password']}")
        layout.addWidget(self.password_label)

        self.email_label = QLabel(f"Mail: {self.password_data['email']}")
        layout.addWidget(self.email_label)

        self.login_label = QLabel(f"Login: {self.password_data['login']}")
        layout.addWidget(self.login_label)

        self.service_label = QLabel(f"Service: {self.password_data['service']}")
        layout.addWidget(self.service_label)

        # кнопка "скопировать" для копирования паролей
        copy_button = QPushButton("Copy")
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
        save_button = QPushButton("Save")
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
        encrypt_button = QPushButton("Encrypt")
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
        self.setLayout(layout)

    def encrypt_password(self):
        """
        Метод для шифрования пароля и обновления данных.
        """
        # Проверка, был ли пароль уже зашифрован
        if self.is_encrypted:
            QMessageBox.warning(self, "Warning", "The password is already encrypted.")
            return

        password = self.password_data["password"]
        fernet = Fernet(self.encryption_key)
        encrypted_password = fernet.encrypt(password.encode()).decode()  # Декодирование в строку
        self.password_data["password"] = encrypted_password
        self.is_encrypted = True  # Установите флаг после успешного шифрования
        print("The password has been successfully encrypted and updated.")
        # Отправляем уведомление
        send_notification("The password is encrypted", "Password successfully encrypted!")

    def copy_password(self):
        """
        Метод для копирования пароля в буфер обмена и отправки уведомления.
        """
        password = self.password_label.text().split(": ")[1]
        pyperclip.copy(password)
        print(f"The password has been successfully copied to the clipboard: {password}")

        # Отправляем уведомление
        send_notification("Copied", "Password successfully copied to clipboard!")

    # def save_password(self)Ж: позволяет пользователю ввести данные для сохранения пароля в текстовый документ
    def save_password(self):
        """
        Метод для сохранения пароля в текстовый документ и отправки уведомления.
        """
        # Позволяет пользователю ввести имя сервиса (открывается окно)
        service_name, ok = QInputDialog.getText(self, "Save password", "Enter the name of the service:")

        if ok:
            self.password_data["service"] = service_name
            print(f"Password for the service {service_name} has been saved.")

        login_name, ok = QInputDialog.getText(self, "Save password", "Enter login:")

        if ok:
            self.password_data["login"] = login_name
            print(f"Password for the service {login_name} has been saved.")

        email_name, ok = QInputDialog.getText(self, "Save password", "Enter mail:")

        if ok:
            self.password_data["email"] = email_name
            print(f"Password for the service {email_name} has been saved.")
            # Отправляем уведомление
            send_notification("Data saved", "Password successfully saved!")


# KeyDisplayDialog(QDialog): Диалоговое окно для отображения ключа шифрования
class KeyDisplayDialog(QDialog):
    def __init__(self, encryption_key):
        """
        Конструктор класса KeyDisplayDialog.

        Parameters:
            encryption_key (str): Ключ шифрования для отображения.
        """
        super().__init__()
        self.setWindowTitle("Encryption key")
        self.setWindowIcon(QIcon('icon.png'))
        layout = QVBoxLayout()
        self.setStyleSheet("""

                        background-color: #0e1621; 
                        color: #FFFFFF; 
                        font-weight: 900;
                        border: none;

                    """)
        key_label = QLabel("Your encryption key:")
        layout.addWidget(key_label)

        key_text_edit = QTextEdit(str(encryption_key))
        key_text_edit.setStyleSheet("""
                background-color: #1f2937;
                color: #FFFFFF;
                border: 2px solid #4a5568;
                border-radius: 5px;
                padding: 10px;
            """)
        layout.addWidget(key_text_edit)

        self.setLayout(layout)


# PasswordSaveDialog(QDialog): Диалоговое окно для отображения сохраненных паролей и связанных с ними данных.
class PasswordSaveDialog(QDialog):
    def __init__(self, passwords_and_data):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Saved passwords and data")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("""
            background-color: #0e1621;
            color: #FFFFFF; 
            font-weight: 900;
            border: none;
        """)

        self.passwords_and_data = passwords_and_data
        print("The 'Saved passwords and data' dialog box is open")

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for password_data in self.passwords_and_data:
            password_block = QTextEdit(self)
            password_block.setStyleSheet("""
                background-color: #1f2937;
                color: #FFFFFF;
                border: 2px solid #4a5568;
                border-radius: 5px;
                padding: 10px;
            """)
            password_text = f"Service: {password_data['service']}\n"
            password_text += f"Password: {password_data['password']}\n"
            password_text += f"Mail: {password_data['email']}\n"
            password_text += f"Login: {password_data['login']}"
            password_block.setPlainText(password_text)
            password_block.setReadOnly(True)
            scroll_layout.addWidget(password_block)

            copy_button = QPushButton("Copy", self)
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
            copy_button.clicked.connect(lambda _, text=password_text: self.copy_text_to_clipboard(text))
            scroll_layout.addWidget(copy_button)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Добавляем кнопку "Скачать"
        download_button = QPushButton("Download", self)
        download_button.setStyleSheet("""
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
        download_button.clicked.connect(self.download_passwords)
        layout.addWidget(download_button)

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
        scroll_area.setStyleSheet(scroll_area_style)

        self.setLayout(layout)

    def copy_text_to_clipboard(self, text):
        pyperclip.copy(text)
        print(f"The text has been successfully copied to the clipboard: {text}")
        send_notification("Copied", "The selection has been successfully copied to the clipboard!")

    def download_passwords(self):
        # Открываем диалоговое окно сохранения файла
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text file (*.txt);;All files (*)")

        # Если пользователь выбрал файл для сохранения
        if file_name:
            try:
                # Открываем выбранный файл для записи
                with open(file_name, "w") as file:
                    # Записываем каждый пароль и связанные с ним данные в файл
                    for password_data in self.passwords_and_data:
                        file.write(f"Service: {password_data['service']}\n")
                        file.write(f"Password: {password_data['password']}\n")
                        file.write(f"Mail: {password_data['email']}\n")
                        file.write(f"Login: {password_data['login']}\n\n")
                print("The file has been successfully saved.")
            except Exception as e:
                print(f"Error when saving a file: {e}")


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
        print("The encryption key has been saved")

    def load_encryption_key(self):
        """
        Метод для загрузки ключа шифрования из файла.
        Если файл не найден, создает новый ключ и сохраняет его.
        """
        try:
            with open("encryption_key.key", "rb") as key_file:
                self.encryption_key = key_file.read().decode()

            print("The application is running, the encryption key has been successfully downloaded")

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
        num_passwords_label = QLabel("How many passwords to generate:")
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
        length_label = QLabel("Enter the length of the password:")
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
                                        border: 1px solid #507EA0

                                    """)

        self.word_input = QLineEdit(self)
        left_layout.addWidget(QLabel("Enter a word:"))
        left_layout.addWidget(self.word_input)
        self.word_input.setStyleSheet(
            "text-decoration: none; border: none; padding: 2px 1px; font-size: 14px; background-color: #2b5378; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 1px solid #507EA0")

        # numbers_checkbox: Флажок для включения цифр в пароль
        self.numbers_checkbox = QCheckBox("Include numbers in the password?")
        left_layout.addWidget(self.numbers_checkbox)

        # special_chars_checkbox: Флажок для включения специальных символов в пароль
        self.special_chars_checkbox = QCheckBox("Include special characters in the password?")
        left_layout.addWidget(self.special_chars_checkbox)

        self.use_uppercase_checkbox = QCheckBox("Use upper case characters?")
        left_layout.addWidget(self.use_uppercase_checkbox)

        self.use_lowercase_checkbox = QCheckBox("Use lower case characters?")
        left_layout.addWidget(self.use_lowercase_checkbox)

        # generate_button: Кнопка для запуска генерации паролей
        generate_button = QPushButton("Generate passwords")
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
        save_button = QPushButton("Generated passwords")
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

        decrypt_button = QPushButton("Decrypt")
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

        # Добавим кнопку "Настройки" на главную страницу
        settings_button = QPushButton("Settings")
        settings_button.setStyleSheet("""
                                      text-decoration: none; 
                                      border: none; 
                                      padding: 5px 1px; 
                                      font-size: 16px; 
                                      background-color: #149dfb; 
                                      color: #fff; 
                                      border-radius: 5px; 
                                      font-family: Calibri; 
                                      font-weight: 900; 
                                      border: 2px solid #507EA0;
                                      """)
        settings_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0; background-color: #74C5FF;"
        settings_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #149dfb; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #507EA0;"
        settings_button.pressed.connect(lambda: settings_button.setStyleSheet(settings_button_style_pressed))
        settings_button.released.connect(lambda: settings_button.setStyleSheet(settings_button_style_released))
        settings_button.clicked.connect(self.show_settings_window)

        left_layout.addWidget(settings_button)
        buttons_container = QHBoxLayout()
        # Добавление контейнера с кнопками в левый layout
        left_layout.addLayout(buttons_container)

        self.setLayout(left_layout)
        self.setWindowTitle("fortify")
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(780, 440)
        self.show()

    def show_settings_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setStyleSheet("background-color: #0e1621; border: none")
        dialog.setFixedSize(180, 160)

        print("The 'Settings' dialog box is open")

        layout = QVBoxLayout(dialog)

        # Кнопка отвечающая за возможности
        capabilities_button = QPushButton("Opportunities", dialog)
        capabilities_button.setStyleSheet("""
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
        capabilities_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2; background-color: #74C5FF;"
        capabilities_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2;"
        capabilities_button.pressed.connect(
            lambda: capabilities_button.setStyleSheet(capabilities_button_style_pressed))
        capabilities_button.released.connect(
            lambda: capabilities_button.setStyleSheet(capabilities_button_style_released))
        capabilities_button.clicked.connect(self.show_fortify_pass_info)

        # Кнопка отвечающая за советы
        tips_button = QPushButton("Tips", dialog)
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

        # кнопка для отображения ключа шифрования в интерфейсе программы
        show_key_button = QPushButton("Encryption key", dialog)
        show_key_button.setStyleSheet("""
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
        # Анимация нажатия кнопки
        show_key_button_style_pressed = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2; background-color: #74C5FF;"
        show_key_button_style_released = "text-decoration: none; border: none; padding: 5px 1px; font-size: 16px; background-color: #0070FF; color: #fff; border-radius: 5px; cursor: pointer; font-family: Calibri; font-weight: 900; border: 2px solid #005CD2;"
        show_key_button.setStyleSheet(show_key_button_style_released)
        show_key_button.pressed.connect(lambda: show_key_button.setStyleSheet(show_key_button_style_pressed))
        show_key_button.released.connect(lambda: show_key_button.setStyleSheet(show_key_button_style_released))
        layout.addWidget(show_key_button)
        show_key_button.clicked.connect(self.show_encryption_key)

        layout.addWidget(capabilities_button)
        layout.addWidget(tips_button)

        dialog.exec()

    def show_encryption_key(self):
        """
        Метод для отображения окна с ключом шифрования.
        """
        print("The 'Encryption Key' dialog box is open")

        key_display_dialog = KeyDisplayDialog(self.encryption_key)
        key_display_dialog.exec()

    def show_tips_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Советы по генерации пароля")
        self.setWindowIcon(QIcon('icon.png'))
        dialog.setFixedSize(500, 400)

        print("Открыто диалоговое окно 'Советы по генерации пароля'")

        dialog.setStyleSheet("background-color: #0e1621; border: none")

        info_text = QTextBrowser(dialog)
        info_text.setOpenExternalLinks(True)

        # Используем HTML для форматирования текста
        info_text.setHtml("""
<html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #FFF;
                margin: 0;
                padding: 0;
            }
            h1 {
                font-size: 20px;
                color: #1f91d5;
                font-weight: bold;
                text-align: center;
                margin-top: 20px;
            }
            h2 {
                font-size: 16px;
                color: #FFF;
                font-weight: bold;
                margin-top: 20px;
            }
            p {
                font-size: 14px;
                color: #FFF;
                margin-bottom: 10px;
            }
            p1 {
                font-size: 14px;
                color: #1f91d5;
                font-weight: bold;
            }
        </style>
    </head>
    
    <body>
        <h1>Password Generation Tips</h1>
        <h2>General Principles:</h2>
        <p>1. Length should be at least <span style="color: #1f91d5;">8</span> characters.</p>
        <p>2. Include various types of characters, such as <span style="color: #1f91d5;">uppercase</span> and <span style="color: #1f91d5;">lowercase</span> letters, numbers, and special symbols.</p>
        <p>3. Should not contain <span style="color: #1f91d5;">personal information</span>, such as: <span style="color: #1f91d5;">name</span>, <span style="color: #1f91d5;">date of birth</span>, or <span style="color: #1f91d5;">phone number</span>.</p>
        <p>4. Should not be <span style="color: #1f91d5;">obvious</span> or easily guessable, for example, <span style="color: #1f91d5;">number sequences</span> or <span style="color: #1f91d5;">keyboard letters</span>.</p>
        <p>5. It's better to use a <span style="color: #1f91d5;">phrase</span> or <span style="color: #1f91d5;">combination of words</span> that are easy to remember but difficult to crack.</p>
        <p>6. <span style="color: #1f91d5;">Regularly change your password</span> and do not use the same password for different accounts.</p>
    </body>
</html>
        """)

        info_text.setGeometry(10, 10, 485, 380)

        dialog.exec()

    # Возможности программы
    def show_fortify_pass_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Возможности Fortify")
        self.setWindowIcon(QIcon('icon.png'))
        dialog.setFixedSize(700, 580)

        print("Открыто диалоговое окно 'Возможности Fortify'")

        dialog.setStyleSheet("background-color: #0e1621; border: none")

        info_text = QTextBrowser(dialog)
        info_text.setOpenExternalLinks(True)
        info_text.setHtml("""
<html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #FFF;
                margin: 0;
                padding: 0;
            }
            h1 {
                font-size: 24px;
                color: #1f91d5;
                font-weight: bold;
                text-align: center;
                margin-top: 20px;
            }
            h2 {
                font-size: 18px;
                color: #1f91d5;
                font-weight: bold;
                margin-top: 20px;
            }
            h3 {
                font-size: 16px;
                color: #FF0000;
                font-weight: bold;
                margin-top: 15px;
            }
            p {
                font-size: 14px;
                margin-bottom: 10px;
            }
            p1 {
                color: #1f91d5;
                font-weight: bold;
            }
            center {
                display: block;
                margin-top: 20px;
                color: #888;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <h1>Fortify Pass Features</h1>
        <h2>1. Generating Multiple Passwords at Once</h2>
        <p>Fortify Pass provides the ability to create not only one, but several unique passwords at once. This is particularly useful when you need to generate a set of passwords for various accounts or services.</p>
        <h2>2. Generating Passwords of User-Defined Length</h2>
        <p>Users can specify the length of the generated password to meet the requirements of specific security systems or their own preferences.</p>
        <h2>3. Integration of Own Phrases and Words into Passwords</h2>
        <p>Fortify Pass allows including your own words or phrases into generated passwords, making them more memorable and personalized.</p>
        <h2>4. Using Various Options for Password Generation</h2>
        <p>The program offers various options for configuring password generation:</p>
        <ul>
            <li>Adding numbers to the password.</li>
            <li>Adding special characters to the password.</li>
            <li>Choosing the generation of characters of different cases.</li>
        </ul>
        <h2>Password Encryption</h2>
        <p>Fortify Pass also offers functionality for encrypting passwords using the "cryptography.fernet" library.</p>
        <ol>
            <li>Upon program launch, the encryption key is automatically loaded into the "encryption_key.key" file.</li>
            <li>A "Encrypt" button is available on the program's main screen, allowing users to encrypt passwords and write them to the "passwords.txt" file.</li>
            <li>There is also a "Decrypt" function that opens a window for decrypting the password using the previously saved encryption key.</li>
        </ol>
        <h3>Attention!</h3>
        <p>It is necessary to ensure the preservation of the encryption key to avoid losing access to encrypted data.</p>
        <center>© Michael Mirmikov</center>
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

        print("Passwords successfully generated")

        if not self.num_passwords_input.text() or not self.length_input.text():
            QMessageBox.critical(self, "Error", "Please select all parameters before generating passwords.")
            return

        # Получите значения параметров
        num_passwords_text = self.num_passwords_input.text()
        length_text = self.length_input.text()
        user_word = self.word_input.text()

        # Проверьте, что пользователь ввел числа для количества паролей и длины
        if not num_passwords_text.isdigit() or not length_text.isdigit():
            QMessageBox.critical(self, "Error",
                                 "Please enter the correct values for the number of passwords and length!")
            return

        if not num_passwords_text or not length_text:
            QMessageBox.critical(self, "Error", "Please enter the number of passwords and the length!")
            return

        self.num_passwords = int(num_passwords_text)
        self.length = int(length_text)
        self.use_numbers = self.numbers_checkbox.isChecked()
        self.use_special_chars = self.special_chars_checkbox.isChecked()
        self.use_uppercase = self.use_uppercase_checkbox.isChecked()
        self.use_lowercase = self.use_lowercase_checkbox.isChecked()
        self.passwords_generated = True

        if not self.use_numbers and not self.use_special_chars and not self.use_uppercase and not self.use_lowercase:
            QMessageBox.warning(self, "Attention", "Please set at least one option to generate passwords!")
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
        print(f"The 'Password and Data' dialog box is open")

        dialog = PasswordDialog(password_data, self.encryption_key)
        dialog.exec()

    # display_passwords(): Метод для отображения сгенерированных паролей и кнопок "Посмотреть".
    def display_passwords(self):
        """
        Метод для отображения сгенерированных паролей и кнопок "Посмотреть".

        Создает виджеты для отображения паролей и кнопок "Посмотреть" в главном окне.
        """
        for i, password_data in enumerate(self.passwords_and_data):
            password_label = QLabel(f"Password: {password_data['password']}")

            view_button = QPushButton("View")
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
            QMessageBox.critical(self, "Error", "Generate the passwords first!")
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
                file.write(f"Service: {password_data['service']}\n")
                file.write(f"Password: {password_data['password']}\n")
                file.write(f"Mail: {password_data['email']}\n")
                file.write(f"Login: {password_data['login']}\n")
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
                    if line.startswith("Service: "):
                        password_data["service"] = line[len("Service: "):]
                    elif line.startswith("Password: "):
                        password_data["password"] = line[len("Password: "):]
                    elif line.startswith("Mail: "):
                        password_data["email"] = line[len("Mail: "):]
                    elif line.startswith("Login: "):
                        password_data["login"] = line[len("Login: "):]
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
        self.setWindowTitle("Decrypt the password")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("""
                           background-color: #0e1621; 
                           color: #FFFFFF; 
                           font-weight: 900;
                           """)

        self.encryption_key = encryption_key

        print("The 'Decrypt Password' dialog box is open")

        # Конвертируем ключ безопасности в строку и устанавливаем его в поле ввода
        self.encryption_key_str = encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key
        self.key_label = QLabel("Enter the security key:")
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

        self.encrypted_text_label = QLabel("Enter the encrypted text:")
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

        decrypt_button = QPushButton("Decrypt the text")
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

            print("The 'Decrypted Text' dialog box is open")

            QMessageBox.information(self, "Decrypted text", f"Decrypted text: {decrypted_text}")
        except Exception as e:
            if "cryptography.fernet.InvalidToken" in str(e):
                QMessageBox.critical(self, "Error", "Failed to decrypt the text. Make sure that the key and the ciphertext are correct.")
            else:
                # Вывести сообщение об ошибке в консоль или лог файл
                print(f"Error in transcribing the text: {e}")
                # или logging.error(f"Ошибка при расшифровке текста: {e}")
                QMessageBox.critical(self, "Error", "An error occurred while decrypting the text. Check the console or security key.")


# В if __name__ == '__main__': блоке приложение и главное окно ex создаются, и производится загрузка ранее сохраненных паролей из файла.
if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = PasswordGeneratorApp()

    # Загрузка ключа шифрования
    ex.load_encryption_key()

    # Загрузка ранее сохраненных паролей
    ex.passwords_and_data = ex.load_passwords_from_file()

    sys.exit(app.exec())
