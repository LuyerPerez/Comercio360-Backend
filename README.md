# 🏪 Sistema de Inventario y Facturación para Negocios de Barrio (Comercio360)

## 📌 Descripción del Proyecto

Este proyecto consiste en el desarrollo de un sistema de inventario orientado a negocios de barrio en Colombia, con el objetivo de facilitar la gestión de productos, ventas y control de stock.

El sistema usa una API unificada con una estructura modular por dominios (usuarios, sesiones, inventario y facturacion), facilitando mantenimiento y evolucion del producto.

---

## 🎯 Objetivo General

Desarrollar un sistema web que permita a pequeños negocios gestionar su inventario y ventas, con la posibilidad de integrar facturación electrónica conforme a los requisitos en Colombia.

---

## 🧠 Arquitectura del Sistema

Por ahora, el sistema usa una **API unificada** para simplificar el desarrollo y el despliegue.

### 🟢 API Unificada de Comercio360
Encargada de:

- Gestión de productos
- Control de inventario
- Registro de ventas
- Gestión de clientes
- Manejo de usuarios
- Facturación y preparación para integración electrónica

### ⚛️ Frontend
Interfaz de usuario desarrollada en React para la interacción con el sistema.

---

## 🛠️ Tecnologías Utilizadas

### Frontend
- React
- Vite
- Tailwind CSS
- Axios

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Base de Datos
- MySQL

---

## 📁 Estructura del Proyecto

```bash
project/
│
├── frontend/                # Aplicación React
├── backend/
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── main.py
│   ├── database.py         # Configuración compartida
│   └── config.py
│
└── README.md
```

## ▶️ Comando para Ejecutar la API Unificada

Desde la raiz del proyecto:

```powershell
cd backend
python -m venv venv
source ./venv/Scripts/activate
pip install -r requirements.txt
pip install --upgrade pip
uvicorn main:app --reload
```

Endpoints de salud:

- API principal: http://127.0.0.1:8000/health

## 📝 Reglas

1. Todo el código debe escribirse en inglés (excepto los comentarios) usando snake_case para funciones y variables (ej. get_document_embeddings), y PascalCase para clases de modelos y esquemas (ej. ArticleCreate). Los nombres de los endpoints en FastAPI deben ser sustantivos en plural y seguir la jerarquía del recurso, por ejemplo, /api/articles/{article_id} en lugar de usar verbos como /get_article.

2. Debes mantener una división estricta entre la lógica de negocio, el acceso a datos y la interfaz de la API para evitar el código "espagueti". En tu proyecto, la carpeta ia/ debe manejar exclusivamente el pipeline de RAG y ChromaDB, mientras que api/ solo gestiona las rutas de FastAPI; nunca realices consultas directas a la base de datos MySQL o realices procesamiento de texto pesado dentro de las funciones de los endpoints.

3. Está prohibido devolver modelos de SQLAlchemy (MySQL) directamente en las respuestas de la API; en su lugar, utiliza siempre Schemas de Pydantic para definir qué datos entran y salen. Esto garantiza que información sensible, como los hashes de contraseñas de los empleados o metadatos internos de ChromaDB, nunca se expongan al frontend y permite que FastAPI genere documentación Swagger precisa automáticamente.

4. Diseña tus endpoints para que sean apátridas (stateless), lo que significa que cada petición del empleado debe contener toda la información necesaria para ser procesada (usando tokens JWT para la autenticación).
