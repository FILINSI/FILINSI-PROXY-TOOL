import os
import threading
import time
from tkinter import filedialog, Tk
import concurrent.futures
import requests
import socket
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("proxy_checker.log"), logging.StreamHandler()])


# Функция проверки прокси
def check_proxy(proxy, results, index, destination_url):
    try:
        proxy = proxy.strip()  # Убираем лишние пробелы и символы новой строки
        logging.debug(f'Starting check for proxy: {proxy}')

        # Добавляем http:// по умолчанию, если не указан протокол
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = "http://" + proxy
            logging.debug(f'Proxy modified to include protocol: {proxy}')

        # Полный HTTP-запрос для измерения времени
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        start_time = time.time()
        response = requests.get(destination_url, proxies=proxies, timeout=10)
        end_time = time.time()

        if response.status_code == 200:
            ping_time = (end_time - start_time) * 1000  # Время в миллисекундах
            results[index] = [proxy, f'{ping_time:.2f} ms', 'Working']
            logging.info(f'Proxy {proxy} is working with full HTTP ping {ping_time:.2f} ms')
        else:
            results[index] = [proxy, 'N/A', 'Unreachable']
            logging.warning(f'Proxy {proxy} is unreachable with status code {response.status_code}')
    except requests.exceptions.ProxyError as e:
        results[index] = [proxy, 'N/A', 'Proxy Error']
        logging.error(f'Proxy {proxy} error: Proxy Error - {str(e)}')
    except requests.exceptions.ConnectTimeout:
        results[index] = [proxy, 'N/A', 'Timeout']
        logging.error(f'Proxy {proxy} error: Connect Timeout')
    except socket.timeout:
        results[index] = [proxy, 'N/A', 'Timeout']
        logging.error(f'Proxy {proxy} error: Socket Timeout')
    except ValueError as ve:
        results[index] = [proxy, 'N/A', 'Invalid Format']
        logging.error(f'Proxy {proxy} error: {ve}')
    except Exception as e:
        results[index] = [proxy, 'N/A', f'Error: {str(e)}']
        logging.error(f'Proxy {proxy} error: {str(e)}')
    finally:
        if results[index] is None:
            results[index] = [proxy, 'N/A', 'Unknown Error']


# Загрузка прокси из файла
def load_proxies_from_file():
    Tk().withdraw()  # Закрыть окно Tkinter
    file_path = filedialog.askopenfilename(title="Select file with proxies")
    if file_path:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    return []


# Функция обновления прогресса проверки прокси
def update_progress(results, proxies, stop_event):
    while not stop_event.is_set():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("{:<30} {:<20} {:<15}".format("Proxy", "Ping (ms)", "Status"))
        print("-" * 70)

        for idx, proxy in enumerate(proxies):
            if results[idx] is None:
                print("{:<30} {:<20} {:<15}".format(proxy, "Calculating...", "Checking..."))
            else:
                print("{:<30} {:<20} {:<15}".format(*results[idx]))

        time.sleep(1)


# Основная функция
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
    ______    ____    __     ____    _   __   _____    ____       
   / ____/   /  _/   / /    /  _/   / | / /  / ___/   /  _/       
  / /_       / /    / /     / /    /  |/ /   \__ \    / /         
 / __/     _/ /    / /___ _/ /    / /|  /   ___/ /  _/ /          
/_/       /___/   /_____//___/   /_/ |_/   /____/  /___/    
                    Proxy Checker v1.0     
    """
    print(ascii_art + '\n' * 5)

    while True:
        print("1: Load proxies from file")
        print("2: Enter proxy manually")

        choice = input("Select an option (1, 2): ")
        proxies = []

        if choice == '1':
            proxies = load_proxies_from_file()
            if not proxies:
                print("No proxies loaded. Returning to menu...")
                continue
        elif choice == '2':
            proxy = input("Enter proxy (format: http://ip:port or ip:port): ")
            proxies.append(proxy)
        else:
            print("Invalid choice!")
            continue

        destination_url = input("Enter the destination URL (default is http://google.com): ") or "http://google.com"

        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)

        results = [None] * len(proxies)
        stop_event = threading.Event()

        progress_thread = threading.Thread(target=update_progress, args=(results, proxies, stop_event))
        progress_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_index = {executor.submit(check_proxy, proxy, results, idx, destination_url): idx for idx, proxy in
                               enumerate(proxies)}

            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    future.result()
                except Exception as exc:
                    logging.error(f'Proxy check generated an exception: {exc}')

        stop_event.set()
        progress_thread.join()

        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art + '\n' * 5)
        print("{:<30} {:<20} {:<15}".format("Proxy", "Ping (ms)", "Status"))
        print("-" * 70)

        working_proxies = []
        for result in results:
            print("{:<30} {:<20} {:<15}".format(*result))
            if result[2].lower() == 'working':
                working_proxies.append(result[0])

        if working_proxies:
            if os.path.exists("working_proxies.txt"):
                os.remove("working_proxies.txt")
        with open("working_proxies.txt", "w") as file:
            stripped_proxies = [proxy.replace('http://', '').replace('https://', '') for proxy in working_proxies]
            file.write("\n".join(stripped_proxies))
            print("\nWorking proxies have been saved to working_proxies.txt")
            print("Select one of the options below to complete your work ")
            continue_choice = input("\nDo you want to check more proxies? (y/n): ")
            if continue_choice.lower() not in ['y']:
                break


if __name__ == '__main__':
    main()
