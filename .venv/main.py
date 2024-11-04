import requests
import concurrent.futures
import time
import os
import sys
import threading
from tkinter import filedialog, Tk

def get_country_flag(country_name):
    country_flags = {
        'Russia': '\U0001F1F7\U0001F1FA',
        'United States': '\U0001F1FA\U0001F1F8',
        'Unknown': '\U0001F3F3',
        # Add more countries as needed
    }
    return country_flags.get(country_name, '\U0001F3F3')

def check_proxy(proxy, lang, results):
    try:
        start_time = time.time()
        response = requests.get('http://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=5)
        end_time = time.time()
        delay = (end_time - start_time) * 1000  # delay in milliseconds
        status = 'Working' if response.status_code == 200 else 'Not Working'
        country = 'Unknown'
        flag = get_country_flag(country)
        if response.status_code == 200:
            ip_info = requests.get(f'http://ip-api.com/json/{proxy.split("//")[-1].split(":")[0]}').json()
            country = ip_info.get('country', 'Unknown' if lang == 'en' else 'Неизвестно')
            flag = get_country_flag(country)
        results.append([proxy, f'{delay:.2f} ms', f'{flag} {country}', status])
    except requests.RequestException:
        results.append([proxy, 'N/A', 'Unknown', 'Not Working'])

def load_proxies_from_file():
    Tk().withdraw()  # Закрыть окно Tkinter
    file_path = filedialog.askopenfilename(title="Select file with proxies")
    if file_path:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file]
    return []

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    # ASCII Art Header
    ascii_art = r"""
    ______    ____    __     ____    _   __   _____    ____       
   / ____/   /  _/   / /    /  _/   / | / /  / ___/   /  _/       
  / /_       / /    / /     / /    /  |/ /   \__ \    / /         
 / __/     _/ /    / /___ _/ /    / /|  /   ___/ /  _/ /          
/_/       /___/   /_____//___/   /_/ |_/   /____/  /___/    
                    Proxy Checker v0.3    
    """
    print(ascii_art + '\n' * 5)


    print("1: 🇬🇧 English")
    print("2: 🇷🇺 Русский")
    lang_choice = input()
    lang = 'en' if lang_choice == '1' else 'ru'

    if lang == 'en':
        print("1: Load proxy as a string")
        print("2: Load proxies from file")
        print("3: Enter proxy with login and password")
        choice = input()
    else:
        print("1: Ввести прокси строкой")
        print("2: Загрузить прокси из файла")
        print("3: Ввести прокси с логином и паролем")
        choice = input()

    proxies = []

    if choice == '1':
        proxy = input(
            "Enter proxy (format: http://ip:port): " if lang == 'en' else "Введите прокси (формат: http://ip:port): ")
        proxies.append(proxy)
    elif choice == '2':
        proxies = load_proxies_from_file()
    elif choice == '3':
        username = input("Enter username: " if lang == 'en' else "Введите имя пользователя: ")
        password = input("Enter password: " if lang == 'en' else "Введите пароль: ")
        ip = input("Enter IP: " if lang == 'en' else "Введите IP: ")
        port = input("Enter port: " if lang == 'en' else "Введите порт: ")
        proxy = f'http://{username}:{password}@{ip}:{port}'
        proxies.append(proxy)
    else:
        print("Invalid choice!" if lang == 'en' else "Неверный выбор!")
        return

    os.system('cls' if os.name == 'nt' else 'clear')  # Очистить экран
    print(ascii_art)  # Показать ASCII Art
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        threads = []
        for i, proxy in enumerate(proxies):
            thread = threading.Thread(target=check_proxy, args=(proxy, lang, results))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    # Print results in a tabular format
    print("{:<30} {:<20} {:<30} {:<15}".format("Proxy", "Ping (ms)", "Country", "Status"))
    print("-" * 100)
    for row in results:
        print("{:<30} {:<20} {:<30} {:<15}".format(*row))

if __name__ == '__main__':
    main()
