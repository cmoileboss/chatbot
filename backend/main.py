
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from routers.user_router import user_router
from routers.auth_router import auth_router
from database.postgres_connection import Base, engine
import models  # Assure l'import de tous les modèles

# Création automatique des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["CookieAuth"] = {
        "type": "apiKey",
        "in": "cookie",
        "name": "access_token",
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"CookieAuth": []}])
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi