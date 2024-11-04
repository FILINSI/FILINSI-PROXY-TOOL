import requests
import concurrent.futures
import time
import os
import threading
from tkinter import filedialog, Tk


# Обновление функций и добавление обработки исключений
def check_proxy(proxy, lang, results, index):
    num_tests = 3
    delays = []
    unstable = False

    for _ in range(num_tests):
        try:
            start_time = time.time()
            response = requests.get("https://httpbin.org/ip", proxies={'http': proxy, 'https': proxy}, timeout=5)
            delay = (time.time() - start_time) * 1000  # задержка в миллисекундах

            if response.status_code != 200:
                raise requests.RequestException("Proxy did not respond correctly.")

            delays.append(delay)

            ip_info = requests.get(f'https://ipapi.co/{proxy.split(":")[0]}/json/').json()
            country = ip_info.get('country_name', 'Unknown' if lang == 'en' else 'Неизвестно')
        except (requests.RequestException, ValueError):
            delays.append(float('inf'))
            unstable = True

    # Calculate the average delay
    valid_delays = [d for d in delays if d != float('inf')]
    average_delay = sum(valid_delays) / len(valid_delays) if valid_delays else float('inf')
    status = 'Working' if not unstable else 'Unstable'
    country = country if valid_delays else 'Unknown'

    results[index] = [proxy, f'{average_delay:.2f} ms' if average_delay != float('inf') else 'N/A', country, status]


def load_proxies_from_file():
    Tk().withdraw()  # Закрыть окно Tkinter
    file_path = filedialog.askopenfilename(title="Select file with proxies")
    if file_path:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
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


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
    ______    ____    __     ____    _   __   _____    ____       
   / ____/   /  _/   / /    /  _/   / | / /  / ___/   /  _/       
  / /_       / /    / /     / /    /  |/ /   \__ \    / /         
 / __/     _/ /    / /___ _/ /    / /|  /   ___/ /  _/ /          
/_/       /___/   /_____//___/   /_/ |_/   /____/  /___/    
                    Proxy Checker v0.15     
    """
    print(ascii_art + '\n' * 5)

    lang_choice = input("Choose language \n 1: 🇬🇧 English \n 2: 🇷🇺 Русский \n ")
    lang = 'en' if lang_choice == '1' else 'ru'

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)

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
            proxy = input(
                "Enter proxy (format: http://ip:port): " if lang == 'en' else "Введите прокси (формат: http://ip:port): ")
            proxies.append(proxy)
        elif choice == '2':
            proxies = load_proxies_from_file()
            if not proxies:
                print(
                    "No proxies loaded. Returning to menu..." if lang == 'en' else "Прокси не загружены. Возвращение в меню...")
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

        results = [None] * len(proxies)
        stop_event = threading.Event()

        progress_thread = threading.Thread(target=update_progress, args=(results, proxies, stop_event))
        progress_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_index = {executor.submit(check_proxy, proxy, lang, results, idx): idx for idx, proxy in
                               enumerate(proxies)}

            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    future.result()
                except Exception as exc:
                    print(f'Proxy check generated an exception: {exc}')

        stop_event.set()
        progress_thread.join()

        continue_choice = input(
            "\nDo you want to check more proxies? (y/n): " if lang == 'en' else "\nХотите проверить ещё прокси? (д/н): ")
        if continue_choice.lower() not in ['y', 'д']:
            break


if __name__ == '__main__':
    main()
