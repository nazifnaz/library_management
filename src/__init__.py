from fastapi import FastAPI

from src.auth.routes import auth_router
from src.db.main import init_db
from src.errors import register_all_errors

version = "v1"

app = FastAPI(
    title="Library Management",
    description="""
    REST API for library management. 
    Librarian/Customer users will be able to manage borrowing/returning books.""",
    version=version,
)

register_all_errors(app)

version_prefix = f"/api/{version}"

app.include_router(auth_router, prefix=f"{version_prefix }/auth", tags=["auth"])
