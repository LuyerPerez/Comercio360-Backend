from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database import Base, engine
from routes.inventory.sessions import router as sessions_router
from routes.inventory.users import router as users_router

app = FastAPI(
    title="Comercio360 API",
    description="API unificada para inventario, usuarios, ventas y facturacion.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(sessions_router)

@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "comercio360-api",
        "mode": "unified",
    }
