@echo off
chcp 65001 >nul

set /p projectName=Введите имя проекта: 

:: Заменяем пробелы на "_"
set "projectName=%projectName: =_%"

mkdir "%projectName%"
cd "%projectName%"

copy "..\create\*.bat" .

echo Проект "%projectName%" был успешно создан и BAT файлы скопированы.

start "" "C:\Program Files\Sublime Text\sublime_text.exe" .

pause
