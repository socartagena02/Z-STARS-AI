# MemoryFlow: REHABILITACIÓN COGNITIVA DIGITAL
MemoryFlow es una plataforma SaaS (Software as a Service), diseñada para centros de rehabilitación multidisciplinados. Utiliza **gamificaciones** y **ML** para mejorar y monitorear funciones cognitivas como la atención, memoria de trabajo e inhibición de impulsos en pacientes de todas las edades.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Estado](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Versión](https://img.shields.io/badge/versión-1.0-green)

# Caracteristicas Principales
- **Modulos de estimulación:** juegos clásicos (Simón dice, Memorice) adaptados para métricas clínicas.
- **Dashboard para los funcionarios:** Visualización de progreso en tiempo real con análisis de latencia y precisión.
- **Accesibilidad con IA:** Integración con **ElevenLabs API** para descripción de audio automáticas, facilitando el uso a personas con dificultades visuales y lectura.
- **Privacidad de datos:** Gestión segura de pacientes mediantes nicknames y segmentación por institución.

# Stack tecnlógico
- **Backend:** Python  3.12 / Django 6.0
- **Frontend:** Javascript, Boostrap 5.8 HTML5 CSS3
- **IA/voz:** ElevenLabs API (Text-to-speech)
- **BD:** SQLite

# Arquitectura de datos & ML
El sistema de captura métrica de **latencia de respuesta** y **tasa de error** mediante eventos asincronicos en JavaScript. Estos datos son procesados por el backend de Django para alimentar:
1. **Modelo predictivo:** Identifica patrones de fatiga cognitiva o mejoras en la atención sostenida.
2. **Dashboard clínico:** Genera visualizaciones de series temporales para el seguimiento del paciente.

# Instalación y configuración

## 1. Clona el repositorio:
```bash
git clone https://github.com/socartagena02/MemoryFlow.git
cd MemoryFlow
```
## 2. Crea el entorno
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac
source venv/bin/activate
```
## 3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 4. Configuración variables del entorno(.env)
Crea un archivo .env y añadele:
```bash
SECRET_KEY='tu_secret_key'
DEBUG=True
ELEVEN_API_KEY='tu_api_key'
VOICE_ID='id_de_voz'
```

## 5. Migraciones 
```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Inicia el servidor
```bash
python manage.py runserver
```
# Vista previa
## Menú de juegos
![paginaInicial1](games/static/games/assets/capturas/menuJuegosSimonDice.png)
![paginaInicial2](games/static/games/assets/capturas/menuJuegosMemorice.png)
![paginaInicial3](games/static/games/assets/capturas/menuJuegosTrazaCamino.png)

## Juegos
### Simon dice
![SimonDiceMenu](games/static/games/assets/capturas/menuDificultadSimonDice.png)
![DificultadFacil](games/static/games/assets/capturas/nivelBasicoSimonDice.png)
![DificultadMediana](games/static/games/assets/capturas/nivelIntermedioSimonDice.png)
![DificultadDificil](games/static/games/assets/capturas/nivelAvanzadoSimonDice.png)

### Memorice
![MemoriceeMenu](games/static/games/assets/capturas/menuDificultadMemorice.png)
![dificultadBasicaMemorice](games/static/games/assets/capturas/dificultadBasicaMemorice.png)
![dificultadBasicaMemorice](games/static/games/assets/capturas/dificultadBasicaMemorice-cardflip.png)
![dificultadBasicaMemorice](games/static/games/assets/capturas/dificultadBasicaMemorice(2).png)
![dificultadBasicaMemorice](games/static/games/assets/capturas/dificultadBasicaMemorice-cardflip(2).png)
![dificultadBasicaMemorice](games/static/games/assets/capturas/dificultadBasicaMemorice-cardflipNivelCompletado.png)

# MockUp
```bash
https://www.figma.com/proto/toq6iZzf5nAo4pHuaAxr9K/MemoryFlow---project?node-id=0-1&t=IRDaqgImEHMa3P6r-1
```

# Roadmap (Próximas versiones)
- [] Implementación del juego "Traza mi camino" (Planificación motora).
- [] Reportes descargables en pdf para padres y médicos.
- [] Modulo de alertas tempranas mediante Machine Learning.

# Autores
- Sofía Cartagena - *Desarrollo, Visión y Arquitectura de Datos*  - [GitHub](https://github.com/socartagena02)