from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from ..db.dbops import get_db, check_user_exists
from models import Contact, pwd_context, GlobalBlackList
from passlib.context import CryptContext
import uuid

userRouter = APIRouter()

class RegisterUserModel(BaseModel):
    name: str
    email: str = Field(default=None, title="Optional email address")
    phone: str
    password: str

class LoginUserModel(BaseModel):
    phone: str
    password: str

def get_password_hash(password: str):
    return pwd_context.hash(password)

@userRouter.post("/register/")
async def register_user(user: RegisterUserModel, db: Session = Depends(get_db)):
    if check_user_exists(db, user.phone):
        raise HTTPException(status_code=400, detail="User already exists")

    user_uuid = str(uuid.uuid4())

    hashed_password = get_password_hash(user.password)

    new_contact = Contact(uuid=user_uuid, 
                          name=user.name, 
                          email=user.email, 
                          phone=user.phone, 
                          password=hashed_password)
    db.add(new_contact)
    db.commit()

    new_global_blacklist = GlobalBlackList(phone=user.phone, 
                                           name=user.name, 
                                           spam=False, 
                                           spam_reports=0)
    db.add(new_global_blacklist)
    db.commit()

    return {"message": "User registered successfully"}



@userRouter.post("/login/")
async def login_user(login_data: LoginUserModel, db: Session = Depends(get_db)):
    user = check_user_exists(db, login_data.phone)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.verify_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = user.generate_token()

    return {"message": "User logged in", "access_token": token}