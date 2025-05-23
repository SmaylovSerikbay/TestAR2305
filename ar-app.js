class WebARApp {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.objectContainer = null;
        this.objectCounter = 0;
        this.isInitialized = false;
        this.placementMode = 'cube';
        this.objects = [];
        
        // Элементы интерфейса
        this.statusElement = document.getElementById('status');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.addCubeBtn = document.getElementById('addCube');
        this.addSphereBtn = document.getElementById('addSphere');
        this.addCylinderBtn = document.getElementById('addCylinder');
        this.clearBtn = document.getElementById('clearObjects');
        
        this.init();
    }
    
    async init() {
        try {
            this.updateStatus('Инициализация AR...');
            
            // Ждем загрузки A-Frame
            await this.waitForAFrame();
            
            // Получаем элементы сцены
            this.scene = document.querySelector('a-scene');
            this.camera = document.querySelector('#arCamera');
            this.objectContainer = document.querySelector('#objectContainer');
            
            // Настраиваем обработчики событий
            this.setupEventListeners();
            
            // Ждем готовности AR
            await this.waitForARReady();
            
            this.updateStatus('AR готов! Наведите камеру на поверхность');
            this.hideLoadingIndicator();
            this.enableControls();
            
            this.isInitialized = true;
            
        } catch (error) {
            console.error('Ошибка инициализации AR:', error);
            this.updateStatus('Ошибка: ' + error.message);
        }
    }
    
    waitForAFrame() {
        return new Promise((resolve) => {
            if (window.AFRAME) {
                resolve();
            } else {
                window.addEventListener('load', resolve);
            }
        });
    }
    
    waitForARReady() {
        return new Promise((resolve) => {
            if (this.scene.hasLoaded) {
                resolve();
            } else {
                this.scene.addEventListener('loaded', resolve);
            }
        });
    }
    
    setupEventListeners() {
        // Кнопки управления
        this.addCubeBtn.addEventListener('click', () => this.setPlacementMode('cube'));
        this.addSphereBtn.addEventListener('click', () => this.setPlacementMode('sphere'));
        this.addCylinderBtn.addEventListener('click', () => this.setPlacementMode('cylinder'));
        this.clearBtn.addEventListener('click', () => this.clearAllObjects());
        
        // События AR
        this.scene.addEventListener('enter-vr', () => {
            this.updateStatus('AR режим активен');
        });
        
        this.scene.addEventListener('exit-vr', () => {
            this.updateStatus('AR режим отключен');
        });
        
        // События касания/клика для размещения объектов
        document.addEventListener('click', (event) => this.handlePlacement(event));
        document.addEventListener('touchend', (event) => this.handlePlacement(event));
        
        // Обработка ошибок
        window.addEventListener('error', (error) => {
            console.error('Ошибка приложения:', error);
            this.updateStatus('Ошибка: ' + error.message);
        });
    }
    
    setPlacementMode(mode) {
        this.placementMode = mode;
        
        // Обновляем активную кнопку
        document.querySelectorAll('.btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (mode === 'cube') this.addCubeBtn.classList.add('active');
        if (mode === 'sphere') this.addSphereBtn.classList.add('active');
        if (mode === 'cylinder') this.addCylinderBtn.classList.add('active');
        
        this.updateStatus(`Режим: ${this.getModeText(mode)}. Коснитесь экрана для размещения`);
    }
    
    getModeText(mode) {
        const modes = {
            'cube': 'Размещение куба',
            'sphere': 'Размещение сферы',
            'cylinder': 'Размещение цилиндра'
        };
        return modes[mode] || mode;
    }
    
    handlePlacement(event) {
        if (!this.isInitialized || !this.placementMode) return;
        
        // Предотвращаем случайные размещения на UI элементах
        if (event.target.closest('.ui-overlay') || event.target.closest('.controls')) {
            return;
        }
        
        event.preventDefault();
        
        // Получаем позицию клика/касания
        const position = this.calculatePlacementPosition(event);
        
        if (position) {
            this.placeObject(this.placementMode, position);
        }
    }
    
    calculatePlacementPosition(event) {
        // Базовая позиция перед камерой
        const cameraEl = this.camera;
        const cameraPosition = cameraEl.getAttribute('position');
        const cameraRotation = cameraEl.getAttribute('rotation');
        
        // Вычисляем позицию на некотором расстоянии перед камерой
        const distance = 2; // 2 метра перед камерой
        const radY = (cameraRotation.y * Math.PI) / 180;
        const radX = (cameraRotation.x * Math.PI) / 180;
        
        const x = cameraPosition.x + Math.sin(radY) * distance;
        const z = cameraPosition.z - Math.cos(radY) * distance;
        const y = cameraPosition.y - Math.tan(radX) * distance - 0.5; // Немного ниже уровня камеры
        
        return { x, y, z };
    }
    
    placeObject(type, position) {
        try {
            const objectId = `object_${type}_${this.objectCounter++}`;
            
            // Создаем объект
            const objectEl = document.createElement('a-entity');
            objectEl.setAttribute('id', objectId);
            objectEl.classList.add('ar-object', 'interactive');
            
            // Устанавливаем геометрию и материал в зависимости от типа
            this.setupObjectGeometry(objectEl, type);
            
            // Устанавливаем позицию
            objectEl.setAttribute('position', `${position.x} ${position.y} ${position.z}`);
            
            // Добавляем анимацию появления
            objectEl.setAttribute('animation__spawn', {
                property: 'scale',
                from: '0 0 0',
                to: '1 1 1',
                dur: 500,
                easing: 'easeOutElastic'
            });
            
            // Добавляем возможность взаимодействия
            objectEl.setAttribute('cursor-listener', '');
            
            // Добавляем в сцену
            this.objectContainer.appendChild(objectEl);
            
            // Сохраняем в массив объектов
            this.objects.push({
                id: objectId,
                type: type,
                element: objectEl,
                position: position,
                timestamp: Date.now()
            });
            
            this.updateStatus(`${this.getModeText(type)} размещен! Объектов: ${this.objects.length}`);
            
            // Воспроизводим звук (если доступен)
            this.playPlacementSound();
            
        } catch (error) {
            console.error('Ошибка размещения объекта:', error);
            this.updateStatus('Ошибка размещения объекта');
        }
    }
    
    setupObjectGeometry(element, type) {
        const scale = this.getRandomScale();
        
        switch (type) {
            case 'cube':
                element.setAttribute('geometry', {
                    primitive: 'box',
                    width: scale,
                    height: scale,
                    depth: scale
                });
                element.setAttribute('mixin', 'cube-material');
                break;
                
            case 'sphere':
                element.setAttribute('geometry', {
                    primitive: 'sphere',
                    radius: scale * 0.5
                });
                element.setAttribute('mixin', 'sphere-material');
                break;
                
            case 'cylinder':
                element.setAttribute('geometry', {
                    primitive: 'cylinder',
                    radius: scale * 0.4,
                    height: scale * 1.2
                });
                element.setAttribute('mixin', 'cylinder-material');
                break;
        }
        
        // Добавляем тень
        element.setAttribute('shadow', 'cast: true; receive: true');
        
        // Добавляем анимацию при наведении
        element.setAttribute('animation__mouseenter', {
            property: 'scale',
            startEvents: 'mouseenter',
            to: `${scale * 1.1} ${scale * 1.1} ${scale * 1.1}`,
            dur: 200
        });
        
        element.setAttribute('animation__mouseleave', {
            property: 'scale',
            startEvents: 'mouseleave',
            to: `${scale} ${scale} ${scale}`,
            dur: 200
        });
    }
    
    getRandomScale() {
        return 0.3 + Math.random() * 0.4; // Размер от 0.3 до 0.7
    }
    
    clearAllObjects() {
        try {
            this.objects.forEach(obj => {
                if (obj.element && obj.element.parentNode) {
                    obj.element.parentNode.removeChild(obj.element);
                }
            });
            
            this.objects = [];
            this.updateStatus('Все объекты удалены');
            
        } catch (error) {
            console.error('Ошибка удаления объектов:', error);
            this.updateStatus('Ошибка удаления объектов');
        }
    }
    
    playPlacementSound() {
        // Создаем простой звуковой сигнал
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
            
        } catch (error) {
            // Звук не критичен, игнорируем ошибки
        }
    }
    
    updateStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
        console.log('AR Status:', message);
    }
    
    hideLoadingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('hidden');
        }
    }
    
    enableControls() {
        this.addCubeBtn.disabled = false;
        this.addSphereBtn.disabled = false;
        this.addCylinderBtn.disabled = false;
        
        // Устанавливаем режим по умолчанию
        this.setPlacementMode('cube');
    }
    
    // Утилиты для отладки
    getObjectsInfo() {
        return {
            total: this.objects.length,
            types: this.objects.reduce((acc, obj) => {
                acc[obj.type] = (acc[obj.type] || 0) + 1;
                return acc;
            }, {}),
            objects: this.objects
        };
    }
}

// Компонент A-Frame для обработки кликов курсора
AFRAME.registerComponent('cursor-listener', {
    init: function () {
        this.el.addEventListener('click', (event) => {
            // Эффект при клике на объект
            this.el.setAttribute('animation__click', {
                property: 'rotation',
                to: '0 360 0',
                dur: 1000,
                easing: 'easeInOutQuad'
            });
        });
    }
});

// Инициализируем приложение когда DOM готов
document.addEventListener('DOMContentLoaded', () => {
    console.log('Инициализация Web AR приложения...');
    window.arApp = new WebARApp();
});

// Экспортируем для глобального доступа
window.WebARApp = WebARApp; 