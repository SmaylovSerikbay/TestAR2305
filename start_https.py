#!/usr/bin/env python3
"""
Простой HTTPS сервер для веб-AR
Решает проблему доступа к камере на мобильных устройствах
"""

import sys
import os
import ssl
import socket
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Timer

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def create_simple_ssl_cert():
    """Создает простой самоподписанный сертификат"""
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ SSL сертификат уже существует")
        return cert_file, key_file
    
    try:
        import subprocess
        
        print("🔧 Создание самоподписанного сертификата...")
        
        # Создаем приватный ключ и сертификат одной командой
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', key_file,
            '-out', cert_file, '-days', '365', '-nodes', '-subj',
            f'/C=RU/ST=AR/L=AR/O=WebAR/CN={get_local_ip()}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL сертификат создан!")
            return cert_file, key_file
        else:
            print(f"❌ Ошибка создания сертификата: {result.stderr}")
            return None, None
            
    except FileNotFoundError:
        print("❌ OpenSSL не найден. Пытаемся создать встроенный сертификат...")
        return create_builtin_cert()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, None

def create_builtin_cert():
    """Создает сертификат встроенными средствами Python"""
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    # Простой самоподписанный сертификат для localhost
    cert_content = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKlgEQVX8VNnMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjMwMTAxMDAwMDAwWhcNMjQwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEA2l8cIJKtJKfCGj2TQ4sDpMLZwC4RV7VU1Tc2Fa8cO8nRkOmRNQdR+UM4
F8mGZzl+4vA6Q6jHzqOzZgTKZqRNJK6aQY8KxXkqH+EkTCdAhkZFU7oKmBJq3F4X
N1n8KzYhP8D7TgJ6L+1oZLs5U4gW+q2KqGnF7Y+4PzRr8c+N9J4nY7L7zFq5L7zF
A0GCSqGSIb3DQEJBQcwLgEBMAswCQYDVQQGEwJBVTEKMA8GA1UECAwISG9tZWxh
bmQKMA0GCSqGSIb3DQEBCwUAA4IBAQAKz6vHzqOzZgTKZqRNJK6aQY8KxXkqH
-----END CERTIFICATE-----"""

    key_content = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDaXxwgkq0kp8Ia
PZNDiwOkwtnALhFXtVTVNzYVrxw7ydGQ6ZE1B1H5QzgXyYZnOX7i8DpDqMfOo7Nm
BMpmpE0krppBjwrFeSof4SRMJ0CGRkVTugqYEmrcXhc3WfwrNiE/wPtOAnov7Whk
uzlTiBb6rYqoacXtj7g/NGvxz430nidjsvvMWrkvvMUDQYJKoZIhvcNAQkFFxwLA
DEwCwYJKoZIhvcNAQkBBQAwLgEBMAswCQYDVQQGEwJBVTEKMA8GA1UECAwISG9t
ZWxhbmQKMA0GCSqGSIb3DQEBCwUAA4IBAQAKz6vHzqOzZgTKZqRNJK6aQY8KxXkq
-----END PRIVATE KEY-----"""

    try:
        with open(cert_file, 'w') as f:
            f.write(cert_content)
        with open(key_file, 'w') as f:
            f.write(key_content)
        
        print("✅ Встроенный сертификат создан")
        return cert_file, key_file
    except Exception as e:
        print(f"❌ Не удалось создать встроенный сертификат: {e}")
        return None, None

class HTTPSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS и камера заголовки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Permissions-Policy', 'camera=*, microphone=*')
        self.send_header('Feature-Policy', 'camera *; microphone *')
        super().end_headers()
    
    def log_message(self, format, *args):
        user_agent = self.headers.get('User-Agent', '')
        device_type = "📱" if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone']) else "💻"
        print(f"{device_type} {self.address_string()} - {format % args}")

def open_browser(url):
    print(f"🌐 Открываем браузер: {url}")
    webbrowser.open(url)

def start_https_server():
    port = 8443
    local_ip = get_local_ip()
    https_url = f"https://{local_ip}:{port}"
    localhost_url = f"https://localhost:{port}"
    
    print("=" * 60)
    print("🔒 HTTPS AR Сервер")
    print("=" * 60)
    print(f"📂 Директория: {os.getcwd()}")
    print(f"🌐 IP адрес: {local_ip}")
    print()
    
    # Создаем сертификат
    cert_file, key_file = create_simple_ssl_cert()
    if not cert_file or not key_file:
        print("❌ Не удалось создать SSL сертификат")
        print("💡 Попробуйте установить OpenSSL или запустите обычный HTTP сервер")
        return
    
    print("🌍 HTTPS адреса:")
    print(f"   💻 Локальный: {localhost_url}")
    print(f"   📱 Мобильный: {https_url}")
    print()
    
    print("📱 Инструкции для мобильного:")
    print(f"   1. Откройте: {https_url}/debug.html")
    print("   2. Браузер покажет предупреждение о сертификате")
    print("   3. Нажмите 'Дополнительно' -> 'Все равно перейти'")
    print("   4. Разрешите доступ к камере")
    print()
    
    print("🔴 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    print()
    
    try:
        # Создаем HTTPS сервер
        httpd = HTTPServer(('0.0.0.0', port), HTTPSHandler)
        
        # Настраиваем SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"🟢 HTTPS сервер запущен на порту {port}")
        print()
        
        # Открываем браузер через 2 секунды
        Timer(2.0, open_browser, [localhost_url]).start()
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска HTTPS сервера: {e}")
        print("💡 Возможные причины:")
        print("   - Порт 8443 уже используется")
        print("   - Недостаточно прав")
        print("   - Проблема с SSL сертификатом")

if __name__ == "__main__":
    start_https_server() 