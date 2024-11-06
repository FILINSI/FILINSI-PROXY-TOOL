# Proxy Checker v1.7

![image](https://github.com/user-attachments/assets/250a05d6-4d6f-4c56-b51e-16361bd49b00)


## 🌐 Description
Proxy Checker is a versatile tool for checking proxy servers, designed for both one-time checks and continuous monitoring. It supports both public and private proxies with authentication. The script determines the country of the proxy server, measures response time through HTTP and socket, and also supports saving working proxies to a file.

This tool can be used to check the availability of a large number of proxies, evaluate their speed, and analyze their reliability. With the console interface, you can easily track the checking process in real-time.

## 🚀 Key Features
- **Supports HTTP and HTTPS proxies**: Simple format (ip:port) and private format with authentication (ip:port:user:password).
- **Ping Measurement**: Accurate ping via socket and HTTP requests to evaluate proxy performance.
- **Automatic Country Detection**: Uses ipapi service to get geolocation.
- **Real-time Proxy Checking**: Convenient console interface based on [Rich](https://github.com/Textualize/rich) for displaying results.
- **Flexible Target URL Selection**: Check accessibility of popular sites (Google, httpbin) or a custom URL.
- **Proxy Monitoring**: Option for continuous monitoring of proxy server availability with user-defined intervals.
- **Logging Results**: Logs all checks for subsequent analysis.

1. **Starting the script**: Go to .venv and open a terminal in the directory
2. Run the script
```bash
python main.py
```
4. **Load proxies**: You can load proxies from a file or enter them manually.
5. **Select Operation Mode**: Single check or monitoring mode is available.
6. **Results display**: Proxy check results are displayed in a table with ping, status and country information.
7. **Saving Working Proxies**: Working proxies are automatically saved to the `working_proxies.txt` file.

## 🛠️ Dependencies
- Python 3.7+
- Rich (for console interface display)
- Requests (for sending HTTP requests)
- ipapi (for determining country by IP)

## 🎓 Installation
Install the necessary dependencies using pip:
```bash
pip install -r requirements.txt
```

## ⚠️ Important
This tool is not intended for improper use of proxy servers. Always respect the rules for using proxies and comply with the laws of your country.

_____________________________________________________________________________________

![image](https://github.com/user-attachments/assets/55594413-7a65-422f-af35-14d7d11afa6b)

## 🌐 Описание

Proxy Checker — это многофункциональный инструмент для проверки прокси-серверов, предназначенный как для одноразовой проверки, так и для длительного мониторинга. Поддерживаются как публичные, так и приватные прокси с авторизацией. Скрипт определяет страну прокси-сервера, измеряет время отклика через HTTP и сокет, а также поддерживает сохранение рабочих прокси в файл.

Этот инструмент можно использовать для проверки доступности большого количества прокси, оценки их скорости и анализа их надёжности. С помощью консольного интерфейса можно легко отслеживать процесс проверки в реальном времени.

## 🚀 Основные возможности
- **Поддержка HTTP и HTTPS прокси**: Простой формат (ip:port) и приватный формат с авторизацией (ip:port:user:password).
- **Измерение скорости отклика**: Точный пинг через сокет и HTTP-запросы для оценки производительности прокси.
- **Автоматическое определение страны прокси**: Используется сервис ipapi для получения геолокации.
- **Проверка прокси в реальном времени**: Реализован удобный консольный интерфейс на базе [Rich](https://github.com/Textualize/rich) для отображения результатов.
- **Гибкость в выборе целевого URL**: Проверка на доступность популярных сайтов (Google, httpbin) или на пользовательский URL.
- **Мониторинг прокси**: Опция для постоянного мониторинга доступности прокси-серверов с пользовательским интервалом.
- **Логирование результатов**: Логи всех проверок сохраняются для последующего анализа.

## 🔧 Как использовать
1. **Запуск скрипта**: Идем в .venv и открываем терминал в директории
2. Запускаем скрипт
```bash
python main.py
```
4. **Загрузка прокси**: Вы можете загрузить прокси из файла или ввести их вручную.
5. **Выбор режима работы**: Доступен режим одноразовой проверки или мониторинга.
6. **Отображение результатов**: Результаты проверки прокси отображаются в виде таблицы с информацией о пинге, статусе и стране.
7. **Сохранение рабочих прокси**: Рабочие прокси автоматически сохраняются в файл `working_proxies.txt`.

## 🛠️ Зависимости
- Python 3.7+
- Rich (для отображения консольного интерфейса)
- Requests (для отправки HTTP-запросов)
- ipapi (для определения страны по IP)


## 🎓 Установка
Установите необходимые зависимости с помощью pip:
```bash
pip install -r requirements.txt
```

## ⚠️ Важно
Этот инструмент не предназначен для неправомерного использования прокси-серверов. Всегда уважайте правила использования прокси и соблюдайте законы вашей страны.

