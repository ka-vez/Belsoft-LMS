from db.database import get_session
from db.models import User, UserCreate

from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["auth"])

TOKEN_EXPIRE_TIME = 20
SECRET_KEY = "JSUEII8297345353905NWFB80NV394H3UGV8BGI39B34"
ALGORITHM = "HS256"
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# initializing the hashing algorithm 
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_session)]

def authenticate_user(email: str, password: str, db):
    user = db.exec(select(User).filter(User.email==email)).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(user_data: dict, expires_delta: timedelta):
    encode = user_data
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("user_id") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user")
        
        return{
            'id': payload.get("user_id"),
            "name": payload.get("name"),
            "email": payload.get("email")
        }
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"could not validate user '{e}'")


@router.post("/login")
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=404, detail="Email or Password Invalid!!")

    token_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,

    }

    # create the token
    token = create_access_token(token_data, timedelta(minutes=TOKEN_EXPIRE_TIME))

    return {"access_token": token, "token_type": "bearer"}

@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_create: UserCreate):
    user_model = User(
        name = user_create.name,
        email = user_create.email,
        hashed_password = bcrypt_context.hash(user_create.hashed_password)
    )

    # adds new user to database
    db.add(user_model)
    db.commit()

    return {"message": "new user created"}


