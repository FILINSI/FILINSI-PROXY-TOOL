import os
import threading
import time
from tkinter import filedialog, Tk
import concurrent.futures
import requests
import socket
import logging
from requests.auth import HTTPProxyAuth

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("proxy_checker.log"), logging.StreamHandler()])


# Функция проверки прокси с двумя этапами
def check_proxy(proxy, results, index):
    def perform_check(proxy, destination_url, auth):
        try:
            start_time = time.time()
            response = requests.get(destination_url, proxies=proxy, timeout=10, auth=auth)
            end_time = time.time()
            ping_time = (end_time - start_time) * 1000
            return response.status_code, ping_time
        except requests.exceptions.RequestException as e:
            logging.warning(f'Proxy check failed for {proxy} with error: {e}')
            return None, None

    proxy = proxy.strip()
    logging.debug(f'Starting check for proxy: {proxy}')

    # Определяем, является ли прокси приватным или публичным
    if proxy.count(":") == 3:
        ip, port, user, password = proxy.split(":")
        proxies = {
            "http": f"http://{user}:{password}@{ip}:{port}",
            "https": f"http://{user}:{password}@{ip}:{port}",
        }
        auth = HTTPProxyAuth(user, password)
        logging.debug(f'Using private proxy with authentication for {ip}:{port}')
    else:
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = "http://" + proxy
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        auth = None
        logging.debug(f'Using public proxy for {proxy}')

    # Первый этап проверки через http://google.com
    status_code, ping_time = perform_check(proxies, "http://google.com", auth)

    if status_code == 200:
        results[index] = [proxy, f'{ping_time:.2f} ms', 'Working (Google)']
        logging.info(f'Proxy {proxy} is working with full HTTP ping {ping_time:.2f} ms via Google')
    else:
        # Второй этап проверки через http://httpbin.org/get, если первый не удался
        status_code, ping_time = perform_check(proxies, "http://httpbin.org/get", auth)
        if status_code == 200:
            results[index] = [proxy, f'{ping_time:.2f} ms', 'Working (HTTPBin)']
            logging.info(f'Proxy {proxy} is working with full HTTP ping {ping_time:.2f} ms via HTTPBin')
        elif status_code == 429:
            results[index] = [proxy, 'N/A', 'Rate Limited']
            logging.warning(f'Proxy {proxy} is rate-limited with status code 429')
        else:
            results[index] = [proxy, 'N/A', 'Unreachable']
            logging.warning(f'Proxy {proxy} is unreachable on both tests')


# Загрузка прокси из файла
def load_proxies_from_file():
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Select file with proxies")
    if file_path:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    return []


# Функция обновления прогресса проверки прокси
def update_progress(results, proxies, stop_event):
    while not stop_event.is_set():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("{:<30} {:<20} {:<25}".format("Proxy", "Ping (ms)", "Status"))
        print("-" * 75)

        for idx, proxy in enumerate(proxies):
            if results[idx] is None:
                print("{:<30} {:<20} {:<25}".format(proxy, "Calculating...", "Checking..."))
            else:
                print("{:<30} {:<20} {:<25}".format(*results[idx]))

        time.sleep(1)


# Функция для запуска тестирования прокси
def run_proxy_tests(proxies, results):
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=update_progress, args=(results, proxies, stop_event))
    progress_thread.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(check_proxy, proxy, results, idx): idx for idx, proxy in enumerate(proxies)}

        for future in concurrent.futures.as_completed(future_to_index):
            try:
                future.result()
            except Exception as exc:
                logging.error(f'Proxy check generated an exception: {exc}')

    stop_event.set()
    progress_thread.join()


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
            proxy = input("Enter proxy (format: ip:port or ip:port:user:password): ")
            proxies.append(proxy)
        else:
            print("Invalid choice!")
            continue

        results = [None] * len(proxies)
        run_proxy_tests(proxies, results)

        # Отображение результатов
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art + '\n' * 5)
        print("{:<30} {:<20} {:<25}".format("Proxy", "Ping (ms)", "Status"))
        print("-" * 75)

        working_proxies = []
        for result in results:
            print("{:<30} {:<20} {:<25}".format(*result))
            if "Working" in result[2]:
                working_proxies.append(result[0])

        # Сохранение рабочих прокси
        if working_proxies:
            with open("working_proxies.txt", "w") as file:
                stripped_proxies = [proxy.replace('http://', '').replace('https://', '') for proxy in working_proxies]
                file.write("\n".join(stripped_proxies))
            print("\nWorking proxies have been saved to working_proxies.txt")

        # Вопрос о повторной проверке
        while True:
            retest_choice = input("\nDo you want to retest proxies? (all/failed/none): ").lower()
            if retest_choice == "all":
                run_proxy_tests(proxies, results)
                break
            elif retest_choice == "failed":
                failed_proxies = [proxies[i] for i, result in enumerate(results) if "Working" not in result[2]]
                if failed_proxies:
                    failed_results = [None] * len(failed_proxies)
                    run_proxy_tests(failed_proxies, failed_results)
                    for i, failed_result in enumerate(failed_results):
                        original_index = proxies.index(failed_proxies[i])
                        results[original_index] = failed_result
                else:
                    print("No failed proxies to retest.")
                break
            elif retest_choice == "none":
                break
            else:
                print("Invalid choice! Please enter 'all', 'failed', or 'none'.")

        continue_choice = input("\nDo you want to check more proxies? (y/n): ")
        if continue_choice.lower() not in ['y']:
            break


if __name__ == '__main__':
    main()
