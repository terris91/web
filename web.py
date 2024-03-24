# Mô tả: Chương trình tìm kiếm các lỗ hổng bảo mật trên trang web sử dụng Python, BeautifulSoup, requests và các thư viện khác

# Nội dung chương trình
import sys
from colorama import Fore, init
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import re
import os
from art import *

init(autoreset=True)

def xss(url, xssPayloadFile):
    try:
        with open(xssPayloadFile, 'r', encoding="utf-8") as file:
            payloads = file.readlines()
    except FileNotFoundError:
        print("Không tìm thấy file payload.")
        return

    try:
        for payload in payloads:
            payload = payload.strip()
            url_with_payload = url + payload
            response = requests.get(url_with_payload)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            if payload in soup.get_text():
                print(Fore.GREEN +"[+] Tìm thấy payload:", payload)
            else:
                print(Fore.RED +"[-] Không tìm thấy payload:", payload)
    except requests.exceptions.RequestException as e:
        print(Fore.RED +"[!] Lỗi:", e)
    input("Nhấn 'q' để thoát.")

def bruteForce(url, error_message,username_file, password_file, param1, param2):
    if not os.path.exists(username_file) or not os.path.exists(password_file):
        print("File không tồntại.")
        return

    with open(username_file, 'r') as user_file:
        usernames = user_file.readlines()
    with open(password_file, 'r') as pass_file:
        passwords = pass_file.readlines()

    for username in usernames:
        username = username.strip()
        for password in passwords:
            password = password.strip()
            data = {param1: username, param2: password}
            response = requests.post(url, data=data)
            soup = BeautifulSoup(response.content, 'html.parser')
            error_tag = soup.find(string=re.compile(error_message))
            if not error_tag:
                print(Fore.GREEN + f"[+] Thành công với user:{username} và password: {password}")
            else:
                print(Fore.RED + f"[!] Thất bại với user: {username} và password: {password}")
    input("Nhấn 'q' để thoát.")

def sqlBul(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    php_urls = re.findall(r'href=[\'"]?([^\'" >]+)', html_content)
    php_urls = [link for link in php_urls if ".php?" in link]
    for php_url in php_urls:
        print(Fore.GREEN+"[+] Tìm thấy URL:",  php_url)
    input("Nhấn 'q' để thoát.")

def dizini_bul(url, hedef_dizinler, set_sleep):
    bulunan_dizinler = set()
    try:
        for dizin in hedef_dizinler:
            hedef = url + "/" + dizin
            response = requests.get(hedef)
            time.sleep(float(set_sleep))
            if response.status_code == 200 and hedef not in bulunan_dizinler:
                print(Fore.GREEN + "[+] Tìm thấy folder:", hedef)
                bulunan_dizinler.add(hedef)
            elif response.status_code == 404 and hedef not in bulunan_dizinler:
                print(Fore.RED + "[!] 404 Not Found:", hedef)

            elif response.status_code == 302 and hedef not in bulunan_dizinler:
                print(Fore.BLUE + "[!] 302 Found:", hedef)

            elif response.status_code == 401 and hedef not in bulunan_dizinler:
                print(Fore.YELLOW + "[!] 401 Unauthorized:", hedef)

    except requests.exceptions as e:
        print("[!] Lỗi:", e)

    print("\nDanh sách các folder đã tìm thấy:")
    for dizin in bulunan_dizinler:
        print("-", dizin)
    print("Tổng cộng: ", len(bulunan_dizinler), "folder đã được tìm thấy.")
    input("Nhấn 'q' để thoát.")

def konsol():
    print("""
    Chức năng:
          1- Tìm kiếm trang quản trị
          2- Tìm kiếm SQL Injection
          3- BruteForce
          4- Tìm kiếm XSS
""")
    print("Vui lòng chọn chức năng (thực hiện bằng cách nhập số chức năng): ")
    choice = input("Chọn: ")
    if choice == "1":
            tprint("tìm kiếm trang quản trị", font="chunky")
            url = input("Vui lòng nhập URL của trang web bạn muốn kiểm tra: ")
            dosya_yolu = input("Vui lòng nhập đường dẫn file chứa danh sách các thư mục: ")
            set_sleep = input("Vui lòng nhập thời gian đợi (giây) trước mỗi yêu cầu GET: ")
            try:
                with open(dosya_yolu, 'r') as dosya:
                    hedef_dizinler = dosya.read().splitlines()
                    dizini_bul(url, hedef_dizinler, set_sleep)
            except FileNotFoundError:
                print(Fore.RED +"File không tồn tại.")
    elif choice == "2":
                tprint("Tìm kiếm SQL Injection", font="small" )
                url = input("Vui lòng nhập URL của trang web bạn muốn kiểm tra: ")
                sqlBul(url)
    elif choice == "3":
                tprint("BruteForce", font="speed" )
                url = input("Vui lòng nhập URL của trang web bạn muốn kiểm tra: ")
                error_message = input("Vui lòng nhập thông báo lỗi (nếu không có, để trống): ")
                param1 = input("Vui lòng nhập tham số 1 (ví dụ: tên đăng nhập): ")
                param2 = input("Vui lòng nhập tham số 2 (ví dụ: mật khẩu): ")
                username_file = input("Vui lòng nhập đường dẫn file chứa tên đăng nhập: ")
                password_file = input("Vui lòng nhập đường dẫn file chứa mật khẩu: ")
                bruteForce(url, error_message,username_file, password_file, param1, param2)
    elif choice == "4":
                tprint("Tìm kiếm XSS", font="chiseled")
                url = input("Vui lòng nhập URL của trang web bạn muốn kiểm tra: ")
                xssPayloadFile = input("Vui lòng nhập đường dẫn file chứa các payload XSS: ")
                xss(url, xssPayloadFile)

def main():
    tprint("gokboru", font="merlin1")
    tprint("BlackHat", font="cybermedium")
    print("meakay")
    print("Chương trình này dùng để học và thử nghiệm, tất cả các hậu quả do người dùng chịu trách nhiệm.")
    sorumluluk = input("Bạn đồng ý rằng bạn chịu trách nhiệm về hành động của mình và người viết chương trình không có bất kỳ phản hồi nào? (Y/N)")
    if sorumluluk.lower() == "y":
        konsol()

if __name__ == "__main__":
    main()