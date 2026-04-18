from fastapi import FastAPI
from database import Base, engine
from inventory_api.routes.sessions import router as sessions_router
from inventory_api.routes.users import router as users_router

app = FastAPI(
    title="Comercio360 API de Inventario",
    description="API principal para inventario, ventas, clientes y operaciones del negocio.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(users_router)
app.include_router(sessions_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
