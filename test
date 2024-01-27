# Инициализация переменных
max_element = 0
second_max_element = 0

# Считывание первого элемента
current_element = int(input("Введите первый элемент последовательности (введите 0 для завершения): "))

while current_element != 0:
    # Обновление максимального и второго по величине элементов
    if current_element > max_element:
        second_max_element = max_element
        max_element = current_element
    elif current_element > second_max_element:
        second_max_element = current_element
    
    # Считывание следующего элемента
    current_element = int(input("Введите следующий элемент последовательности (введите 0 для завершения): "))

# Вывод результата
print("Второй по величине элемент в последовательности:", second_max_element)
