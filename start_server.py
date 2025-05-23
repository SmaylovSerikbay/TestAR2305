#!/usr/bin/env python3
"""
Простой HTTP сервер для веб-AR приложения
Автоматически определяет Python версию и запускает сервер
"""

import sys
import os
import webbrowser
import time
from threading import Timer

def open_browser(url):
    """Открывает браузер через несколько секунд после запуска сервера"""
    print(f"🌐 Открываем браузер: {url}")
    webbrowser.open(url)

def start_server():
    """Запускает HTTP сервер в зависимости от версии Python"""
    
    port = 8000
    host = 'localhost'
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    print("🚀 Запуск веб-сервера для AR приложения")
    print("=" * 60)
    print(f"📂 Директория: {os.getcwd()}")
    print(f"🌍 URL: {url}")
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
    
    # Информация о страницах
    pages = [
        ("Базовая версия AR", "index.html"),
        ("Продвинутая версия AR", "advanced.html")
    ]
    
    print("📄 Доступные страницы:")
    for name, file in pages:
        if os.path.exists(file):
            print(f"   ✅ {name}: {url}/{file}")
        else:
            print(f"   ❌ {name}: {file} (не найден)")
    
    print()
    print("🔴 Для остановки сервера нажмите Ctrl+C")
    print("=" * 60)
    print()
    
    # Открываем браузер через 2 секунды
    Timer(2.0, open_browser, [url]).start()
    
    try:
        if sys.version_info[0] == 3:
            # Python 3
            import http.server
            import socketserver
            
            class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def end_headers(self):
                    # Добавляем CORS заголовки для AR
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    # Заголовки для HTTPS на localhost
                    self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
                    self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                    super().end_headers()
                
                def log_message(self, format, *args):
                    # Логирование запросов
                    print(f"📡 {self.address_string()} - {format % args}")
            
            with socketserver.TCPServer((host, port), CustomHTTPRequestHandler) as httpd:
                print(f"🟢 Сервер запущен на {url}")
                print(f"📱 Для тестирования AR откройте ссылку на мобильном устройстве")
                print(f"💻 Для настольного компьютера используйте веб-камеру")
                print()
                httpd.serve_forever()
                
        else:
            # Python 2 (устарело, но для совместимости)
            import SimpleHTTPServer
            import SocketServer
            
            Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            with SocketServer.TCPServer((host, port), Handler) as httpd:
                print(f"🟢 Сервер запущен на {url}")
                print("⚠️  Внимание: Используется Python 2. Рекомендуется обновиться до Python 3!")
                httpd.serve_forever()
                
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Ошибка: Порт {port} уже используется!")
            print(f"💡 Попробуйте:")
            print(f"   - Закрыть другие приложения, использующие порт {port}")
            print(f"   - Изменить порт в скрипте")
            print(f"   - Использовать команду: python -m http.server {port+1}")
        else:
            print(f"❌ Ошибка сервера: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    # Дополнительная информация
    print("💡 Советы для лучшей работы AR:")
    print("   • Используйте Chrome или Firefox для лучшей совместимости")
    print("   • Разрешите доступ к камере")
    print("   • Обеспечьте хорошее освещение")
    print("   • Используйте ровные контрастные поверхности")
    print("   • Избегайте отражающих поверхностей")
    print()
    
    start_server() 