from db.database import init_db
from routers import auth, book

from fastapi import FastAPI


init_db()

app = FastAPI()

app.include_router(auth.router)
app.include_router(book.router)



