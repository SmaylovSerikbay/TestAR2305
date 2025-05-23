#!/usr/bin/env python3
"""
HTTP сервер для веб-AR приложения с поддержкой мобильных устройств
Доступен по локальной сети для тестирования на телефоне
"""

import sys
import os
import webbrowser
import socket
import qrcode
import io
import base64
from threading import Timer

def get_local_ip():
    """Получает локальный IP адрес компьютера"""
    try:
        # Подключаемся к внешнему адресу, чтобы определить локальный IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def generate_qr_code(url):
    """Генерирует QR код для URL"""
    try:
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Создаем ASCII версию QR кода
        modules = qr.get_matrix()
        ascii_qr = ""
        for row in modules:
            line = ""
            for module in row:
                line += "██" if module else "  "
            ascii_qr += line + "\n"
        
        return ascii_qr
    except:
        return "QR код недоступен (установите: pip install qrcode)"

def open_browser(url):
    """Открывает браузер через несколько секунд после запуска сервера"""
    print(f"🌐 Открываем браузер: {url}")
    webbrowser.open(url)

def start_mobile_server():
    """Запускает HTTP сервер, доступный из локальной сети"""
    
    port = 8000
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{port}"
    localhost_url = f"http://localhost:{port}"
    
    print("=" * 70)
    print("📱 Запуск веб-сервера для мобильных устройств")
    print("=" * 70)
    print(f"📂 Директория: {os.getcwd()}")
    print(f"🔧 Python: {sys.version}")
    print()
    
    # Проверяем наличие файлов
    files_to_check = ['index.html', 'ar-app.js', 'style.css']
    missing_files = [f for f in files_to_check if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Ошибка: Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Убедитесь, что вы находитесь в правильной директории!")
        return
    
    print("✅ Все необходимые файлы найдены!")
    print()
    
    # Информация о доступе
    print("🌍 URLs для доступа:")
    print(f"   💻 На этом компьютере: {localhost_url}")
    print(f"   📱 На мобильном устройстве: {local_url}")
    print()
    
    # Информация о страницах
    pages = [
        ("Базовая версия AR", "index.html"),
        ("Продвинутая версия AR", "advanced.html")
    ]
    
    print("📄 Доступные страницы:")
    for name, file in pages:
        if os.path.exists(file):
            print(f"   ✅ {name}:")
            print(f"      💻 {localhost_url}/{file}")
            print(f"      📱 {local_url}/{file}")
        else:
            print(f"   ❌ {name}: {file} (не найден)")
    
    print()
    print("📱 QR код для быстрого доступа с телефона:")
    print("   Отсканируйте QR код камерой телефона:")
    print()
    
    # Генерируем QR код
    qr_code = generate_qr_code(local_url)
    print(qr_code)
    print(f"   URL: {local_url}")
    print()
    
    # Инструкции для мобильного
    print("📲 Инструкции для мобильного устройства:")
    print("   1. Убедитесь, что телефон подключен к той же Wi-Fi сети")
    print("   2. Откройте браузер на телефоне (Chrome рекомендуется)")
    print(f"   3. Введите адрес: {local_ip}:8000")
    print("   4. Или отсканируйте QR код выше")
    print("   5. Разрешите доступ к камере")
    print("   6. Наведите камеру на ровную поверхность")
    print()
    
    print("🔴 Для остановки сервера нажмите Ctrl+C")
    print("=" * 70)
    print()
    
    # Открываем браузер на компьютере через 2 секунды
    Timer(2.0, open_browser, [localhost_url]).start()
    
    try:
        if sys.version_info[0] == 3:
            import http.server
            import socketserver
            
            class MobileHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def end_headers(self):
                    # CORS заголовки для AR
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    
                    # Заголовки для камеры на мобильных
                    self.send_header('Permissions-Policy', 'camera=*, microphone=*')
                    self.send_header('Feature-Policy', 'camera *; microphone *')
                    
                    # Заголовки безопасности
                    self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
                    self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                    
                    super().end_headers()
                
                def log_message(self, format, *args):
                    # Логирование с указанием устройства
                    user_agent = self.headers.get('User-Agent', '')
                    device_type = "📱" if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone']) else "💻"
                    print(f"{device_type} {self.address_string()} - {format % args}")
            
            # Запускаем сервер, доступный из локальной сети
            with socketserver.TCPServer(("0.0.0.0", port), MobileHTTPRequestHandler) as httpd:
                print(f"🟢 Сервер запущен и доступен в локальной сети!")
                print(f"💻 Локальный доступ: {localhost_url}")
                print(f"📱 Мобильный доступ: {local_url}")
                print()
                httpd.serve_forever()
                
        else:
            print("❌ Требуется Python 3 для работы с мобильными устройствами!")
            
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Ошибка: Порт {port} уже используется!")
            print(f"💡 Остановите предыдущий сервер (Ctrl+C) и попробуйте снова")
            print(f"   Или используйте другой порт: python start_mobile_server.py")
        else:
            print(f"❌ Ошибка сервера: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Веб-AR сервер для мобильных устройств")
    print()
    print("💡 Советы для AR на мобильном:")
    print("   • Используйте Chrome или Safari")
    print("   • Разрешите доступ к камере")
    print("   • Обеспечьте хорошее освещение")
    print("   • Используйте контрастные поверхности")
    print("   • Держите телефон устойчиво")
    print("   • Медленно перемещайте камеру для калибровки")
    print()
    
    start_mobile_server() 