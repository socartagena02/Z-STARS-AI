# Z-STARS AI 

Z-STARS AI es una plataforma web de estimulación cognitiva orientada a centros de rehabilitación que utiliza ejercicios gamificados para evaluar funciones ejecutivas como memoria de trabajo, atención sostenida y control inhibitorio.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Estado](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Versión](https://img.shields.io/badge/versión-2.0-green)

# Características 
- Registro y procesamiento de métricas cognitivas en tiempo real
- Backend API para almacenamiento y análisis de datos
- Clasificación de desempeño mediante modelo de Machine Learning
- Visualización de datos en dashboard interactivo

# Tecnologías
- Python
- Django
- JavaScript
- Bootstrap
- SQLite
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

## Flujo del sistema

1. El usuario interactúa con los minijuegos en el frontend
2. Los datos son enviados al backend mediante peticiones HTTP
3. El backend procesa y almacena las métricas en la base de datos
4. Se ejecuta un modelo de Machine Learning para evaluar el desempeño
5. Los resultados se visualizan en el dashboard
6. Se puede generar un análisis adicional mediante modelo LLM

## Endpoints
### Vistas principales

| Método | Endpoint | Descripción |
|--------|----------|------------|
| GET | `/` | Inicio de sesión |
| GET | `/dashboard/` | Panel con métricas y análisis de pacientes |
| GET | `/memorice/` | Juego memorice |
| GET | `/simon_dice/` | Juego simon dice |
| GET | `/menu_juegos` | Menú principal |
| GET | `/logout` | Cierre de sesión |

### API REST

| Método | Endpoint | Descripción |
|--------|----------|------------|
| POST | `/puntos/` | Registra una partida y ejecuta el modelo de Machine Learning |
| POST | `/api/analizar/` | Genera análisis de rendimiento utilizando modelo LLM |

> Nota: Algunos endpoints no siguen convención REST completa y serán normalizados en futuras versiones.

# Vista previa

## Videos 
Próximamente disponibles

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

## Machine Learning
- **Modelo:** Random Forest
- **Uso:** Clasificación de resultados de usuarios.
- **Entrada:** puntaje, fallos, tiempo total, tiempo de reacción, nivel de dificultad.
- **Salida:** clasificación del estado cognitivo (ej: estable, mejora, deterioro).

El modelo Random Forest es cargado desde el backend y ejecutado en tiempo de solicitud para clasificar el desempeño del usuario. Actualmente no se encuentra desacoplado como microservicio.


# Estructura
Z-STARS-AI/
├── core/
├── games/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── ml/
│   ├── templates/
│   └── static/
├── manage.py
└── requirements.txt

## Autenticación

El sistema utiliza autenticación basada en sesiones de Django para proteger rutas como el dashboard y la gestión de datos.

# Instalación y ejecución

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
## 4. migraciones
```bash
python manage.py migrate
```
## 5. Iniciar servidor
```bash
python manage.py runserver
```

# Roadmap (Próximas versiones)
- [ ] Implementación del juego "Traza mi camino"
- [ ] Reportes descargables en PDF
- [ ] Módulo de alertas tempranas mediante ML
- [ ] Autenticación de usuarios (JWT)
- [ ] Mejora en validaciones de datos
- [ ] Migración a PostgreSQL
- [ ] Asistente virtual con IA para apoyo al paciente.

# Autores
- Sofía Cartagena
Backend Developer (Python | Django | SQL) - [GitHub](https://github.com/socartagena02)
