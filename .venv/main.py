import requests
import concurrent.futures
import time
import os
import threading
import keyboard
from tkinter import filedialog, Tk
from urllib.parse import urlparse


def get_country_flag(country_name):
    country_flags = {
        'Russia': '\U0001F1F7\U0001F1FA',
        'United States': '\U0001F1FA\U0001F1F8',
        'Unknown': '\U0001F3F3',
    }
    return country_flags.get(country_name, '\U0001F3F3')


def check_proxy(proxy, lang, results, index, stop_event):
    unstable = False
    while not stop_event.is_set():
        try:
            start_time = time.time()
            response = requests.get('http://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=5)
            delay = (time.time() - start_time) * 1000  # задержка в миллисекундах

            if response.status_code == 200:
                parsed_url = urlparse(proxy)
                ip_address = parsed_url.hostname
                ip_info = requests.get(f'http://ip-api.com/json/{ip_address}').json()
                country = ip_info.get('country', 'Unknown' if lang == 'en' else 'Неизвестно')
                flag = get_country_flag(country)
                status = 'Working' if not unstable else 'Unstable'
            else:
                country, flag, status = 'Unknown', get_country_flag('Unknown'), 'Not Working'
                unstable = True

            results[index] = [proxy, f'{delay:.2f} ms', f'{flag} {country}', status]
        except requests.RequestException:
            results[index] = [proxy, 'N/A', 'Unknown', 'Unstable']
            unstable = True

        time.sleep(5)  # Проверять прокси каждые 5 секунд


def load_proxies_from_file():
    Tk().withdraw()  # Закрыть окно Tkinter
    file_path = filedialog.askopenfilename(title="Select file with proxies")
    if file_path:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file]
    return []


def update_progress(results, proxies, stop_event):
    while not stop_event.is_set():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("{:<30} {:<20} {:<30} {:<15}".format("Proxy", "Ping (ms)", "Country", "Status"))
        print("-" * 100)

        for idx, proxy in enumerate(proxies):
            if results[idx] is None:
                print("{:<30} {:<20} {:<30} {:<15}".format(proxy, "Checking...", "N/A", "N/A"))
            else:
                print("{:<30} {:<20} {:<30} {:<15}".format(*results[idx]))

        time.sleep(0.3)

        if keyboard.is_pressed('enter'):
            stop_event.set()
            break


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
    ______    ____    __     ____    _   __   _____    ____       
   / ____/   /  _/   / /    /  _/   / | / /  / ___/   /  _/       
  / /_       / /    / /     / /    /  |/ /   \__ \    / /         
 / __/     _/ /    / /___ _/ /    / /|  /   ___/ /  _/ /          
/_/       /___/   /_____//___/   /_/ |_/   /____/  /___/    
                    Proxy Checker v0.9     
    """
    print(ascii_art + '\n' * 5)

    # Выбор языка только один раз
    lang_choice = input("Choose language \n 1: 🇬🇧 English \n 2: 🇷🇺 Русский \n ")
    lang = 'en' if lang_choice == '1' else 'ru'

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)

        # Переход на страницу выбора действия с прокси
        if lang == 'en':
            print("1: Load proxy as a string")
            print("2: Load proxies from file")
            print("3: Enter proxy with login and password")
        else:
            print("1: Ввести прокси строкой")
            print("2: Загрузить прокси из файла")
            print("3: Ввести прокси с логином и паролем")

        choice = input("Select an option (1, 2, 3): ")
        proxies = []

        if choice == '1':
            proxy = input("Enter proxy (format: http://ip:port): " if lang == 'en' else "Введите прокси (формат: http://ip:port): ")
            proxies.append(proxy)
        elif choice == '2':
            proxies = load_proxies_from_file()
            if not proxies:
                print("No proxies loaded. Returning to menu..." if lang == 'en' else "Прокси не загружены. Возвращение в меню...")
                continue
        elif choice == '3':
            username = input("Enter username: " if lang == 'en' else "Введите имя пользователя: ")
            password = input("Enter password: " if lang == 'en' else "Введите пароль: ")
            ip = input("Enter IP: " if lang == 'en' else "Введите IP: ")
            port = input("Enter port: " if lang == 'en' else "Введите порт: ")
            proxy = f'http://{username}:{password}@{ip}:{port}'
            proxies.append(proxy)
        else:
            print("Invalid choice!" if lang == 'en' else "Неверный выбор!")
            continue

        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)

        # Создать пустые результаты
        results = [None] * len(proxies)
        stop_event = threading.Event()

        # Запустить поток для обновления прогресса
        progress_thread = threading.Thread(target=update_progress, args=(results, proxies, stop_event))
        progress_thread.start()

        # Запустить проверку прокси в многопоточном режиме
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for index, proxy in enumerate(proxies):
                executor.submit(check_proxy, proxy, lang, results, index, stop_event)

        # Дождаться завершения потока обновления прогресса
        progress_thread.join()

        # Запросить у пользователя, хочет ли он продолжить работу или завершить программу
        continue_choice = input("\nDo you want to check more proxies? (y/n): " if lang == 'en' else "\nХотите проверить ещё прокси? (д/н): ")
        if continue_choice.lower() not in ['y', 'д']:
            break


if __name__ == '__main__':
    main()
