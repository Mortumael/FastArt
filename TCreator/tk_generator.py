import csv
import os
from datetime import datetime

FILENAME = "testcases.csv"

# Проверяем, есть ли файл, если нет — создаём с заголовками
if not os.path.exists(FILENAME):
    with open(FILENAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ID", "Где проводился тест",
            "Предусловия", "Описание функционала",
            "Шаги", "Ожидаемый результат",
            "Что будет после шагов", "Приоритет", "Дата создания"
        ])

def generate_test_case():
    """Задаёт вопросы и возвращает список с данными тест-кейса."""
    test_env = input("1. Где проводился тест? → ").strip()
    preconditions = input("2. Какие предусловия были? → ").strip()
    description = input("3. Опиши общую проблему или функционал → ").strip()
    steps = input("4. Опиши шаги проверки → ").strip()
    expected = input("5. Что ожидаешь от поведения? → ").strip()
    after_steps = input("6. Что произойдет после выполнения шагов? → ").strip()

    priority_map = {"1": "1П", "2": "2П", "3": "3П", "4": "4П"}
    while True:
        priority_input = input("7. Приоритет (1/2/3/4) → ").strip()
        if priority_input in priority_map:
            priority = priority_map[priority_input]
            break
        else:
            print("Введите 1, 2, 3 или 4")

    # Генерируем ID
    test_id = f"TC_{int(datetime.now().timestamp())}"

    return [
        test_id, test_env, preconditions, description,
        steps, expected, after_steps, priority,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]

def main():
    print("=== Генератор тест-кейсов ===")
    while True:
        case = generate_test_case()

        # Сохраняем в CSV
        with open(FILENAME, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(case)

        print(f"\n✅ ТК {case[0]} сохранён в {FILENAME}")

        cont = input("\nДобавить ещё один? (y/n) → ").strip().lower()
        if cont != "y":
            print("Завершение работы генератора.")
            break

if __name__ == "__main__":
    main()
