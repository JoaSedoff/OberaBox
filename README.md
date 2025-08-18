# OberáBox: Plataforma de Gestión de Depósitos

## Descripción General

OberáBox es un prototipo de plataforma web de tipo cliente-servidor, diseñado para simular la gestión y estimación de espacios en un negocio de depósitos. El sistema ofrece una calculadora de volumen interactiva para los usuarios finales y un panel de administración para el negocio, con un sistema de notificaciones en tiempo real.

---

## Características Principales

* **Calculadora Interactiva**: Permite a los usuarios seleccionar objetos predefinidos o ingresar ítems personalizados para calcular el volumen total requerido.
* **Gestión de Registros**: Los datos de contacto del cliente y el detalle de la solicitud son almacenados en una base de datos.
* **Panel de Administración**: Un área protegida con autenticación permite al administrador visualizar un historial completo de todos los registros de solicitudes.
* **Notificaciones en Tiempo Real**: Las nuevas solicitudes de clientes activan una notificación automatizada a través de un bot de Telegram, proporcionando información instantánea al administrador.
* **Arquitectura Robusta**: El sistema está completamente contenerizado utilizando Docker para asegurar portabilidad y fácil despliegue.

---

## Tecnologías Utilizadas

### Frontend
* HTML, CSS, JavaScript
* Bootstrap 5 (Bootswatch Lux)
* Librerías de iconos como Font Awesome y Material Symbols

### Backend
* Python 3
* Flask

### Base de Datos
* MariaDB
* phpMyAdmin para gestión

### Notificaciones
* API de Telegram
* `python-telegram-bot`

### Despliegue
* Docker
* Servidor Virtual Privado (VPS) con sistema operativo Debian

---

## Cómo Empezar

### Requisitos Previos

Para ejecutar este proyecto de forma local, necesitas tener instalado:
* Docker y Docker Compose.
* Git.

### Instalación y Ejecución

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://www.youtube.com/watch?v=3GymExBkKjE](https://www.youtube.com/watch?v=3GymExBkKjE)
    cd [nombre del repositorio]
    ```

2.  **Configurar las variables de entorno:**
    * Crea un archivo `.env` en el directorio raíz.
    * Incluye las variables necesarias para la conexión a la base de datos, el token del bot de Telegram y otras configuraciones.

3.  **Levantar los contenedores con Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    Este comando construirá y ejecutará todos los servicios definidos en el archivo `docker-compose.yml`.

4.  **Acceder a la aplicación:**
    * La aplicación estará disponible en `http://localhost:PUERTO`, donde `PUERTO` es el puerto que hayas mapeado en tu `docker-compose.yml`.
    * El panel de phpMyAdmin para la base de datos estará disponible en `http://localhost:PUERTO_PHPMYADMIN`.

