#!/usr/bin/env python3
"""
Простой HTTPS сервер для веб-AR
"""

import ssl
import os
import socket
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Timer

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def create_ssl_cert():
    """Создает SSL сертификат с помощью OpenSSL"""
    import subprocess
    
    cert_file = 'server.pem'
    
    if os.path.exists(cert_file):
        print("✅ SSL сертификат уже существует")
        return cert_file
    
    try:
        print("🔧 Создание SSL сертификата...")
        
        # Простая команда для создания self-signed сертификата
        cmd = [
            'openssl', 'req', '-new', '-x509', '-keyout', cert_file, '-out', cert_file,
            '-days', '365', '-nodes', '-subj', '/CN=localhost'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL сертификат создан!")
            return cert_file
        else:
            print(f"❌ Ошибка OpenSSL: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ OpenSSL не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

class HTTPSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Permissions-Policy', 'camera=*, microphone=*')
        super().end_headers()
    
    def log_message(self, format, *args):
        user_agent = self.headers.get('User-Agent', '')
        device_type = "📱" if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone']) else "💻"
        print(f"{device_type} {self.address_string()} - {format % args}")

def start_https_server():
    port = 8443
    local_ip = get_local_ip()
    https_url = f"https://{local_ip}:{port}"
    
    print("🔒 HTTPS AR Сервер")
    print(f"🌐 IP: {local_ip}")
    print()
    
    # Создаем сертификат
    cert_file = create_ssl_cert()
    if not cert_file:
        print("❌ Не удалось создать сертификат")
        print("💡 Установите OpenSSL: https://slproweb.com/products/Win32OpenSSL.html")
        return
    
    print(f"📱 Адрес для мобильного: {https_url}")
    print(f"📄 Диагностика: {https_url}/debug.html")
    print()
    print("⚠️  На мобильном будет предупреждение - нажмите 'Все равно перейти'")
    print()
    
    try:
        httpd = HTTPServer(('0.0.0.0', port), HTTPSHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"🟢 HTTPS сервер запущен на порту {port}")
        print("🔴 Для остановки нажмите Ctrl+C")
        print()
        
        Timer(2.0, lambda: webbrowser.open(f"https://localhost:{port}")).start()
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    start_https_server() 