# Api de finanzas en FastAPI y Alpha Vantage API
Proyecto de desarrollo de una API de finanzas y predicción consumiendo la API Alpha Vantage, usando las librerías Uvicorn, Requests, Prophet y FastAPI, incluyendo además pruebas unitarias usando la librería Pytest para estas funcionalidades; todo esto contenerizado mediante Docker.

## Requisitos
- Docker y Docker Compose
- Python 3.8+

# Environment
- **ALPHA_API_KEY:** API key del servicio Apha Vantage `https://www.alphavantage.co/support/#api-key`
- **SYMBOL:** Símbolo o acción financiera por defecto, por ejemplo AAPL (Apple)

### Instalar dependencias
`pip install -r requirements.txt`

### Construir la imagen
`docker-compose build`

### Levantar todo
`docker-compose up -d`

## Acceso
- **API**: `http://localhost:8000`
- **Swagger**: `http://localhost:8000/docs`

## Ejecución de pruebas unitarias

### Ejecutar pruebas unitarias
`python -m pytest .`

### Visualizar cobertura
Carpeta `htmlcov` en la raiz del proyecto, y abrir en el navegador el archivo `index.html`