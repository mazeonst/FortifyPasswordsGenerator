from cryptography.fernet import Fernet

def generate_key():
    # Генерация ключа пользователя
    key = Fernet.generate_key()
    with open("ключ.txt", "wb") as key_file:
        key_file.write(key)
    print("Ваш ключ для расшифровки данных сохранен в файле 'ключ.txt'.")
    return key

def encrypt_text(key, text):
    # Создание объекта Fernet для шифрования
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    return encrypted_text

def decrypt_text(key, encrypted_text):
    # Создание объекта Fernet для расшифровки
    fernet = Fernet(key)
    decrypted_text = fernet.decrypt(encrypted_text)
    return decrypted_text.decode()

# Генерируем ключ, если его нет
try:
    with open("ключ.txt", "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = generate_key()

# Введите текст для шифрования
text_to_encrypt = input("Введите текст для шифрования: ")

# Шифруем текст
encrypted_text = encrypt_text(key, text_to_encrypt)

# Запись зашифрованного текста в файл
with open("зашифрованный_текст.txt", "wb") as file:
    file.write(encrypted_text)

print("Текст успешно зашифрован и сохранен в файле 'зашифрованный_текст.txt'.")

# Расшифровываем и выводим текст в консоли
decrypted_text = decrypt_text(key, encrypted_text)
print("Расшифрованный текст:", decrypted_text)
