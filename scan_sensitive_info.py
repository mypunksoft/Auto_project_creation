import os
import sys
import subprocess
import re
from pathlib import Path

# Инструменты для проверки
TOOLS = {
    "python": ["black", "pylint", "mypy", "bandit"],
    "cpp": ["cppcheck"],
}

# Список регулярных выражений для поиска чувствительных данных
patterns = {
    "API key": r"(api[-_]*key|apikey|api\s*secret)[\s:=]*[a-zA-Z0-9\-_]{32,}",
    "Password": r"(password|pass|passwd|secret)[\s:=]*['\"]?([a-zA-Z0-9!@#$%^&*]{8,})['\"]?",
    "Login": r"(login|username|user)[\s:=]*['\"]?(\w+)['\"]?",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"secret[ -_]key[\s:=]*['\"]?[a-zA-Z0-9/+=]{40}['\"]?",
}

IGNORED_FOLDERS = {"node_modules", ".git", "__pycache__"}


def run_tool(command):
    """Запуск инструмента и получение результатов"""
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr:
            return f"Ошибка при запуске {command[0]}: {result.stderr}"
        return result.stdout
    except FileNotFoundError:
        return f"Инструмент {command[0]} не найден. Установите его с помощью соответствующего способа."


def generate_report(results, output_dir, file_name):
    """Генерация отчёта"""
    os.makedirs(output_dir, exist_ok=True)  # Создать директорию, если она не существует
    output_file = os.path.join(output_dir, f"{file_name}_report.txt")
    with open(output_file, "w", encoding="utf-8") as report:
        for tool, result in results.items():
            report.write(f"\n{'='*40}\nРезультаты {tool}:\n{'='*40}\n")
            report.write(result)
    print(f"Отчёт сохранён в: {output_file}")


def scan_file(file_path):
    """Сканирование файла на наличие чувствительных данных и комментариев"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    sensitive_data_found = {}
    comments_found = []

    # Поиск чувствительных данных
    for label, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            sensitive_data_found[label] = matches

    # Поиск комментариев, игнорируя цветовые коды
    comments = re.findall(r"(#.*|//.*|/\*[\s\S]*?\*/)", content)

    # Фильтрация комментариев, исключая те, которые содержат цветовые коды
    valid_comments = []
    for comment in comments:
        # Исключаем комментарии, содержащие цветовые коды, такие как #RRGGBB или #RRGGBBAA
        if not re.search(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})", comment):
            valid_comments.append(comment)

    if valid_comments:
        comments_found = valid_comments

    return sensitive_data_found, comments_found


def process_file(file_path, file_type, output_dir):
    """Обрабатывает отдельный файл по его типу"""
    results = {}
    file_name = Path(file_path).stem  # Имя файла без пути и расширения

    # Проверка инструментами, если для типа файла они заданы
    if file_type in TOOLS and TOOLS[file_type]:
        for tool in TOOLS[file_type]:
            results[tool] = run_tool([tool, file_path])

    # Поиск чувствительных данных и комментариев
    sensitive_data, comments = scan_file(file_path)

    # Добавление результатов о чувствительных данных
    if sensitive_data:
        findings_text = "\nНайдены чувствительные данные:\n"
        for label, matches in sensitive_data.items():
            findings_text += f"  - {label}: {matches}\n"
        results["Проверка чувствительных данных"] = findings_text
    else:
        results["Проверка чувствительных данных"] = (
            "\nЧувствительных данных не найдено.\n"
        )

    # Добавление результатов о комментариях
    if comments:
        comments_text = "\nНайдены комментарии:\n"
        for comment in comments:
            comments_text += f"  - {comment}\n"
        results["Проверка комментариев"] = comments_text
    else:
        results["Проверка комментариев"] = "\nКомментарии не найдены.\n"

    # Генерация отчёта для файла
    generate_report(results, output_dir, file_name)


def scan_directory(directory_path):
    """Сканирование директории на поддерживаемые файлы и обработка каждого"""
    supported_extensions = {
        ".py": "python",
        ".cpp": "cpp",
    }

    # Директория для сохранения отчётов
    report_dir = os.path.join(directory_path, "reports")

    for root, dirs, files in os.walk(directory_path):
        # Удаляем из списка папки, которые нужно игнорировать
        dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

        for file in files:
            ext = Path(file).suffix
            if ext in supported_extensions:
                file_path = os.path.join(root, file)
                print(f"Обработка файла: {file_path}")
                process_file(file_path, supported_extensions[ext], report_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Получение директории из аргументов
        directory_path = sys.argv[1]
        scan_directory(directory_path)
    else:
        print("Использование: python script.py <directory_path>")
