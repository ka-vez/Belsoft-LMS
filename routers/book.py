from db.database import get_session
from db.models import Book, BookCreate 
from routers.auth import get_current_user

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select
from typing import Annotated


router = APIRouter(prefix="/books", tags=["books"])

db_dependency = Annotated[Session, Depends(get_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/available")
async def all_available_books(db: db_dependency):
    books = db.exec(select(Book).filter(Book.borrowed == False)).all()
    return [book.model_dump(exclude={'borrowed_user_id'}) for book in books]

@router.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(db: db_dependency, book_create: BookCreate):
    # creates the book and checks against validations
    book_model = Book(**book_create.model_dump())
    
    # saves the book to the database
    db.add(book_model)
    db.commit()

    return {"message": "new book created"}

@router.post("/borrow-book/{book_id}")
async def borrow_a_book(book_id: int, db: db_dependency, user: user_dependency):
    # gets a book by its id
    book =  db.get(Book, book_id)

    # checks if book with id exists in the database
    if not book:
        raise HTTPException(status_code=404, detail="Book does not exists")

    # checks if book has been borrowed
    if book.borrowed == True:
        raise HTTPException(status_code=404, detail="Book has been borrowed")

    # changes book borrowed_value to true
    book.borrowed = True
    book.borrowed_user_id = user.get("id")

    # updates the db
    db.add(book)
    db.commit()

    return {"message": f"You have successfully borrowed '{book.name}'"}

@router.post("/return-book/{book_id}")
async def return_a_book(book_id: int, db: db_dependency, user: user_dependency):
    # gets a book by its id
    book =  db.get(Book, book_id)

    # checks if book with id exists in the database
    if not book:
        raise HTTPException(status_code=404, detail="Book does not exists")

    # checks if book has been borrowed
    if book.borrowed != True:
        raise HTTPException(status_code=404, detail="Book has not been borrowed")

    # checks if the user who is returning the book is actually the person that borrowed the book
    if book.borrowed_user_id != user.get('id'):
        raise HTTPException(status_code=401, detail="You did not borrow this book")
    
    # changes book borrowed_value to False
    book.borrowed = False
    book.borrowed_user_id = None

    # updates the db
    db.add(book)
    db.commit()

    return {"message": f"You have successfully returned '{book.name}'"}

