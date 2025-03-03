from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.borrowings.routes import router as borrowing_router
from src.db.main import init_db
from src.errors import register_all_errors

version = "v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Library Management",
    description="""
    REST API for library management. 
    Librarian/Customer users will be able to manage borrowing/returning books.""",
    version=version,
    lifespan=lifespan
)



register_all_errors(app)

version_prefix = f"/api/{version}"

app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(book_router, prefix=f"{version_prefix}", tags=["book"])
app.include_router(borrowing_router, prefix=f"{version_prefix}/borrowings", tags=["borrowing"])

