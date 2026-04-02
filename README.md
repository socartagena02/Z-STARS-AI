# Z-STARS AI 
Z-STARS AI es una plataforma web de estimulación cognitiva orientada a centros de rehabilitación que utiliza ejercicios gamificados para evaluar funciones ejecutivas como memoria de trabajo, atención sostenida y control inhibitorio.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Estado](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Versión](https://img.shields.io/badge/versión-1.0-green)

# Características 
- Ejercicios de memoria interactivos
- Registro de métricas cognitivas
- Gestión de pacientes
- Dashboard de progreso

# Tecnologías
- Python
- Django
- JavaScript
- Bootstrap
- SQLite
- ElevenLabs
- scikit-learn (Random Forest)
- Chart.js

# Arquitectura de datos
Z-STARS AI registra eventos cognitivos en tiempo real desde el frontend mediante JavaScript asíncrono.

Las métricas capturadas incluyen:
- Latencia de respuesta
- Tasa de error
- Tiempo de sesión
- Nivel de dificultad

La arquitectura está diseñada para que estas métricas sean procesadas por el backend en Django, 
permitiendo alimentar:

1. **Modelo predictivo**
   - Detecta fatiga cognitiva
   - Identifica mejoras en la atención sostenida

2. **Dashboard clínico**
   - Visualización de progreso
   - Series temporales de desempeño
   
## Videos 
Proximamente disponibles

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
https://www.figma.com/design/toq6iZzf5nAo4pHuaAxr9K/Z-STARS-AI---project?node-id=0-1&t=4tem9TwkkyUhzmkG-1
```
# Estructura
Z-STARS-AI/
 ├── core/
 ├── games/
       ├── templates/
       ├── static/
 ├── manage.py
 └── requirements.txt

# Instalación y configuración

## 1. Clonar repositorio
```bash
git clone https://github.com/socartagena02/Z-STARS-AI.git
cd Z-STARS-AI
```
## 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac
source venv/bin/activate
```
## 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
## 4. Configurar variables de entorno
```bash
SECRET_KEY=''
DEBUG=True
ELEVEN_API_KEY=''
VOICE_ID=''
```
## 5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```
## 6. Iniciar servidor
```bash
python manage.py runserver
```
# Roadmap (Próximas versiones)
- [ ] Implementación del juego "Traza mi camino"
- [ ] Reportes descargables en PDF
- [ ] Módulo de alertas tempranas mediante ML
- [X] Integración del backend en Django para persistencia de métricas.
- [X] Implementación del Dashboard clínico con series temporales.
- [X] Desarrollo del modelo predictivo para detección de fatiga cognitiva.
- [ ] Asistente virtual con IA para apoyo al paciente.
# Autores
- Sofía Cartagena - *Desarrollo, Visión y Arquitectura de Datos*  - [GitHub](https://github.com/socartagena02)
