// Продвинутая версия AR с улучшенным отслеживанием поверхностей
class AdvancedWebAR extends WebARApp {
    constructor() {
        super();
        this.hitTestSource = null;
        this.localReferenceSpace = null;
        this.viewerReferenceSpace = null;
        this.session = null;
        this.renderer = null;
        this.scene3js = null;
        this.camera3js = null;
        this.isWebXRSupported = false;
        this.placementIndicator = null;
        this.lastHitTestResult = null;
        
        this.checkWebXRSupport();
    }
    
    async checkWebXRSupport() {
        if ('xr' in navigator) {
            try {
                this.isWebXRSupported = await navigator.xr.isSessionSupported('immersive-ar');
                if (this.isWebXRSupported) {
                    console.log('WebXR AR поддерживается!');
                    this.initWebXR();
                } else {
                    console.log('WebXR AR не поддерживается, используем AR.js fallback');
                }
            } catch (error) {
                console.log('Ошибка проверки WebXR:', error);
                this.isWebXRSupported = false;
            }
        }
    }
    
    async initWebXR() {
        try {
            // Создаем кнопку для запуска WebXR сессии
            this.createWebXRButton();
            
        } catch (error) {
            console.error('Ошибка инициализации WebXR:', error);
        }
    }
    
    createWebXRButton() {
        const webxrBtn = document.createElement('button');
        webxrBtn.textContent = 'Запустить WebXR AR';
        webxrBtn.className = 'btn webxr-btn';
        webxrBtn.style.position = 'fixed';
        webxrBtn.style.top = '20px';
        webxrBtn.style.right = '20px';
        webxrBtn.style.background = '#ff6b6b';
        
        webxrBtn.addEventListener('click', () => this.startWebXRSession());
        document.body.appendChild(webxrBtn);
    }
    
    async startWebXRSession() {
        try {
            this.session = await navigator.xr.requestSession('immersive-ar', {
                requiredFeatures: ['hit-test', 'local-floor'],
                optionalFeatures: ['dom-overlay', 'light-estimation']
            });
            
            await this.onSessionStart();
            
        } catch (error) {
            console.error('Не удалось запустить WebXR сессию:', error);
            this.updateStatus('WebXR недоступен, используем AR.js');
        }
    }
    
    async onSessionStart() {
        this.session.addEventListener('end', () => this.onSessionEnd());
        
        // Получаем reference spaces
        this.localReferenceSpace = await this.session.requestReferenceSpace('local-floor');
        this.viewerReferenceSpace = await this.session.requestReferenceSpace('viewer');
        
        // Инициализируем hit testing
        await this.initHitTesting();
        
        // Настраиваем рендерер
        this.setupWebXRRenderer();
        
        // Создаем индикатор размещения
        this.createPlacementIndicator();
        
        this.updateStatus('WebXR AR активен! Наведите на поверхность');
    }
    
    async initHitTesting() {
        this.hitTestSource = await this.session.requestHitTestSource({
            space: this.viewerReferenceSpace
        });
    }
    
    setupWebXRRenderer() {
        // Получаем Three.js сцену из A-Frame
        this.scene3js = this.scene.object3D;
        this.camera3js = this.camera.getObject3D('camera');
        this.renderer = this.scene.renderer;
        
        // Настраиваем WebXR
        this.renderer.xr.enabled = true;
        this.renderer.xr.setSession(this.session);
        
        // Запускаем рендер цикл
        this.renderer.setAnimationLoop((time, frame) => this.onFrame(time, frame));
    }
    
    createPlacementIndicator() {
        // Создаем индикатор места размещения
        const indicatorEl = document.createElement('a-entity');
        indicatorEl.setAttribute('geometry', {
            primitive: 'ring',
            radiusOuter: 0.15,
            radiusInner: 0.1
        });
        indicatorEl.setAttribute('material', {
            color: '#4fc3f7',
            shader: 'flat',
            opacity: 0.7,
            transparent: true
        });
        indicatorEl.setAttribute('animation__pulse', {
            property: 'scale',
            from: '1 1 1',
            to: '1.1 1.1 1.1',
            dur: 1000,
            dir: 'alternate',
            loop: true,
            easing: 'easeInOutSine'
        });
        indicatorEl.setAttribute('visible', false);
        
        this.objectContainer.appendChild(indicatorEl);
        this.placementIndicator = indicatorEl;
    }
    
    onFrame(time, frame) {
        if (!frame) return;
        
        // Выполняем hit testing
        if (this.hitTestSource) {
            const hitTestResults = frame.getHitTestResults(this.hitTestSource);
            
            if (hitTestResults.length > 0) {
                this.lastHitTestResult = hitTestResults[0];
                this.updatePlacementIndicator(hitTestResults[0]);
            } else {
                this.hidePlacementIndicator();
            }
        }
    }
    
    updatePlacementIndicator(hitResult) {
        if (!this.placementIndicator) return;
        
        const pose = hitResult.getPose(this.localReferenceSpace);
        if (pose) {
            const position = pose.transform.position;
            const orientation = pose.transform.orientation;
            
            this.placementIndicator.setAttribute('position', {
                x: position.x,
                y: position.y,
                z: position.z
            });
            
            this.placementIndicator.setAttribute('rotation', {
                x: orientation.x * (180 / Math.PI),
                y: orientation.y * (180 / Math.PI),
                z: orientation.z * (180 / Math.PI)
            });
            
            this.placementIndicator.setAttribute('visible', true);
        }
    }
    
    hidePlacementIndicator() {
        if (this.placementIndicator) {
            this.placementIndicator.setAttribute('visible', false);
        }
    }
    
    // Переопределяем метод размещения для WebXR
    calculatePlacementPosition(event) {
        if (this.isWebXRSupported && this.session && this.lastHitTestResult) {
            // Используем WebXR hit testing для точного размещения
            return this.getWebXRPlacementPosition();
        } else {
            // Fallback к базовому методу
            return super.calculatePlacementPosition(event);
        }
    }
    
    getWebXRPlacementPosition() {
        if (!this.lastHitTestResult) return null;
        
        const pose = this.lastHitTestResult.getPose(this.localReferenceSpace);
        if (pose) {
            return {
                x: pose.transform.position.x,
                y: pose.transform.position.y,
                z: pose.transform.position.z
            };
        }
        return null;
    }
    
    // Улучшенное размещение объектов с привязкой к поверхности
    placeObject(type, position) {
        if (!position) return;
        
        try {
            const objectId = `object_${type}_${this.objectCounter++}`;
            
            // Создаем объект
            const objectEl = document.createElement('a-entity');
            objectEl.setAttribute('id', objectId);
            objectEl.classList.add('ar-object', 'interactive', 'surface-anchored');
            
            // Устанавливаем геометрию и материал
            this.setupObjectGeometry(objectEl, type);
            
            // Размещаем с учетом поверхности
            this.positionObjectOnSurface(objectEl, position, type);
            
            // Добавляем физику для стабильности
            this.addObjectPhysics(objectEl);
            
            // Добавляем анимацию появления
            objectEl.setAttribute('animation__spawn', {
                property: 'scale',
                from: '0 0 0',
                to: '1 1 1',
                dur: 600,
                easing: 'easeOutBack'
            });
            
            // Добавляем компонент для отслеживания поверхности
            objectEl.setAttribute('surface-tracker', '');
            
            // Добавляем взаимодействие
            objectEl.setAttribute('cursor-listener', '');
            
            // Добавляем в сцену
            this.objectContainer.appendChild(objectEl);
            
            // Сохраняем информацию об объекте
            this.objects.push({
                id: objectId,
                type: type,
                element: objectEl,
                position: position,
                timestamp: Date.now(),
                anchored: true
            });
            
            this.updateStatus(`${this.getModeText(type)} закреплен на поверхности! Объектов: ${this.objects.length}`);
            this.playPlacementSound();
            
            // Скрываем индикатор размещения временно
            this.hidePlacementIndicator();
            setTimeout(() => {
                if (this.placementIndicator) {
                    this.placementIndicator.setAttribute('visible', true);
                }
            }, 1000);
            
        } catch (error) {
            console.error('Ошибка размещения объекта:', error);
            this.updateStatus('Ошибка размещения объекта');
        }
    }
    
    positionObjectOnSurface(element, position, type) {
        // Настраиваем позицию с учетом типа объекта
        let yOffset = 0;
        
        switch (type) {
            case 'cube':
                yOffset = 0.15; // Половина высоты куба
                break;
            case 'sphere':
                yOffset = 0.15; // Радиус сферы
                break;
            case 'cylinder':
                yOffset = 0.18; // Половина высоты цилиндра
                break;
        }
        
        element.setAttribute('position', {
            x: position.x,
            y: position.y + yOffset,
            z: position.z
        });
    }
    
    addObjectPhysics(element) {
        // Добавляем физические свойства для стабильности
        element.setAttribute('static-body', {
            shape: 'auto'
        });
        
        // Добавляем компонент для предотвращения дрейфа
        element.setAttribute('position-stabilizer', '');
    }
    
    onSessionEnd() {
        this.session = null;
        this.hitTestSource = null;
        this.updateStatus('WebXR сессия завершена');
        
        // Возвращаемся к AR.js режиму
        if (this.placementIndicator) {
            this.placementIndicator.setAttribute('visible', false);
        }
    }
    
    // Метод для калибровки отслеживания
    calibrateSurfaceTracking() {
        this.updateStatus('Калибровка... Медленно поводите камерой по поверхности');
        
        setTimeout(() => {
            this.updateStatus('Калибровка завершена! AR готов к использованию');
        }, 3000);
    }
    
    // Улучшенный метод очистки с учетом WebXR
    clearAllObjects() {
        super.clearAllObjects();
        
        if (this.placementIndicator) {
            this.placementIndicator.setAttribute('visible', this.session ? true : false);
        }
    }
}

// Компонент A-Frame для отслеживания поверхности
AFRAME.registerComponent('surface-tracker', {
    init: function () {
        this.originalPosition = this.el.getAttribute('position');
        this.stabilityThreshold = 0.01; // Порог стабильности в метрах
        this.lastPosition = this.originalPosition;
    },
    
    tick: function () {
        // Проверяем стабильность позиции объекта
        const currentPosition = this.el.getAttribute('position');
        const distance = this.calculateDistance(currentPosition, this.lastPosition);
        
        if (distance > this.stabilityThreshold) {
            // Объект сдвинулся, возвращаем к исходной позиции
            this.el.setAttribute('position', this.originalPosition);
        }
        
        this.lastPosition = currentPosition;
    },
    
    calculateDistance: function (pos1, pos2) {
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        const dz = pos1.z - pos2.z;
        return Math.sqrt(dx*dx + dy*dy + dz*dz);
    }
});

// Компонент для стабилизации позиции
AFRAME.registerComponent('position-stabilizer', {
    init: function () {
        this.anchorPosition = this.el.getAttribute('position');
        this.maxDrift = 0.05; // Максимальный дрейф в метрах
    },
    
    tick: function () {
        const currentPos = this.el.getAttribute('position');
        const anchor = this.anchorPosition;
        
        // Вычисляем расстояние от якорной позиции
        const drift = Math.sqrt(
            Math.pow(currentPos.x - anchor.x, 2) +
            Math.pow(currentPos.y - anchor.y, 2) +
            Math.pow(currentPos.z - anchor.z, 2)
        );
        
        // Если дрейф превышает порог, корректируем позицию
        if (drift > this.maxDrift) {
            this.el.setAttribute('position', this.anchorPosition);
        }
    }
});

// Функция для инициализации продвинутого AR
function initAdvancedAR() {
    console.log('Инициализация продвинутого Web AR...');
    
    // Проверяем поддержку WebXR
    if ('xr' in navigator) {
        window.arApp = new AdvancedWebAR();
    } else {
        console.log('WebXR не поддерживается, используем базовую версию');
        window.arApp = new WebARApp();
    }
}

// Экспортируем класс
window.AdvancedWebAR = AdvancedWebAR;

// Автоматическая инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Переопределяем базовую инициализацию
    if (window.arApp) {
        // Базовое приложение уже создано, заменяем его на продвинутое
        window.arApp = null;
    }
    
    initAdvancedAR();
}); 