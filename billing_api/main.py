from fastapi import FastAPI

app = FastAPI(
    title="Comercio360 API de Facturacion",
    description="API de facturacion para generar facturas y preparar datos para factura electronica.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
