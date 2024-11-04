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
def check_proxy(proxy, results, index):
    try:
        proxy = proxy.strip()  # Убираем лишние пробелы и символы новой строки
        logging.debug(f'Starting check for proxy: {proxy}')

        # Добавляем http:// по умолчанию, если не указан протокол
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = "http://" + proxy
            logging.debug(f'Proxy modified to include protocol: {proxy}')

        # Извлечение IP и порта из прокси
        proxy_address = proxy.split("//")[-1]
        if "@" in proxy_address:
            proxy_address = proxy_address.split("@")[-1]  # Извлекаем часть с IP:порт
        ip_port = proxy_address.split(":")
        if len(ip_port) < 2:
            raise ValueError(
                f"Missing port in proxy address: {proxy}. Please provide both IP and port in the format ip:port.")

        ip, port = ip_port[0], int(ip_port[-1])
        logging.debug(f'Extracted IP: {ip}, Port: {port}')

        # Пинг IP-адреса через socket
        start_time = time.time()
        sock = socket.create_connection((ip, port), timeout=5)
        sock.close()
        ping_time = (time.time() - start_time) * 1000  # Конвертация в миллисекунды
        logging.debug(f'Ping time for {proxy}: {ping_time:.2f} ms')

        # Проверяем подключение через прокси с помощью HTTP запроса
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        response = requests.get("http://ipinfo.io", proxies=proxies, timeout=5)
        if response.status_code == 200:
            results[index] = [proxy, f'{ping_time:.2f} ms', 'Working']
            logging.info(f'Proxy {proxy} is working with ping {ping_time:.2f} ms')
        else:
            results[index] = [proxy, f'{ping_time:.2f} ms', 'Unreachable']
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
        # Убедимся, что результат всегда обновляется, чтобы прогресс отобразился
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

        time.sleep(1)  # Увеличиваем время задержки для обновления экрана, чтобы избежать слишком частых обновлений


# Основная функция
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
    ______    ____    __     ____    _   __   _____    ____       
   / ____/   /  _/   / /    /  _/   / | / /  / ___/   /  _/       
  / /_       / /    / /     / /    /  |/ /   \__ \    / /         
 / __/     _/ /    / /___ _/ /    / /|  /   ___/ /  _/ /          
/_/       /___/   /_____//___/   /_/ |_/   /____/  /___/    
                    Proxy Checker v1.8     
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

        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)

        results = [None] * len(proxies)
        stop_event = threading.Event()

        progress_thread = threading.Thread(target=update_progress, args=(results, proxies, stop_event))
        progress_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_index = {executor.submit(check_proxy, proxy, results, idx): idx for idx, proxy in
                               enumerate(proxies)}

            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    future.result()
                except Exception as exc:
                    logging.error(f'Proxy check generated an exception: {exc}')

        stop_event.set()
        progress_thread.join()

        # Отображаем финальный результат после завершения всех проверок
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art + '\n' * 5)
        print("{:<30} {:<20} {:<15}".format("Proxy", "Ping (ms)", "Status"))
        print("-" * 70)

        for result in results:
            print("{:<30} {:<20} {:<15}".format(*result))

        continue_choice = input("\nDo you want to check more proxies? (y/n): ")
        if continue_choice.lower() not in ['y']:
            break


if __name__ == '__main__':
    main()
