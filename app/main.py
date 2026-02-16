from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import finanzas_routes

app = FastAPI(title="Financial API")


# CORS (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar rutas
app.include_router(finanzas_routes.router)
