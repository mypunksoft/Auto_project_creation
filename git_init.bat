@echo off
chcp 65001 >nul

if not exist "reports" (
    echo Папка "reports" не найдена. Проверьте код перед загрузкой на git!
    pause
    exit /b
)

:: Создаём .gitignore или добавляем в него исключения
if not exist ".gitignore" (
    echo *.json > .gitignore
    echo reports/ >> .gitignore
    echo .gitignore >> .gitignore
    echo Файл .gitignore создан и добавлены исключения для .json, папки reports и самого .gitignore.
) else (
    :: Добавляем исключение для *.json
    findstr /C:"*.json" .gitignore >nul
    if %errorlevel% neq 0 (
        echo *.json>> .gitignore
        echo Исключение для json файлов добавлено в .gitignore.
    )

    :: Добавляем исключение для папки reports
    findstr /C:"reports/" .gitignore >nul
    if %errorlevel% neq 0 (
        echo reports/>> .gitignore
        echo Исключение для папки reports добавлено в .gitignore.
    )

    :: Добавляем исключение для самого .gitignore
    findstr /C:".gitignore" .gitignore >nul
    if %errorlevel% neq 0 (
        echo .gitignore>> .gitignore
        echo Исключение для файла .gitignore добавлено.
    )
)

set /p gitUrl=Введите URL репозитория Git: 

git init

git remote add origin %gitUrl%

git status

echo Какие файлы вы хотите добавить?
set /p files=Введите путь к файлам через пробел или если нужны все поставьте .: 

git add %files%

echo Указанные файлы добавлены.

set /p commitMessage=Введите сообщение для коммита: 

git commit -m "%commitMessage%"

git push -u origin master

echo Репозиторий успешно обновлён.
pause
