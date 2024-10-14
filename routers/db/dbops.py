from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import LocalSession
from models import GlobalBlackList, Contact
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from fastapi import Depends
from security import oauth2_scheme
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update

dbRouter = APIRouter()

class ReportUserModel(BaseModel):
    phone: str
    name: str

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

class SearchUserModel(BaseModel):
    name: str

class SearchPhoneModel(BaseModel):
    phone: str

def check_user_exists(db: Session, phone: str):
    return db.query(Contact).filter(Contact.phone == phone).first()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
        if uuid is None:
            raise credentials_exception
        return uuid
    except JWTError:
        raise credentials_exception

@dbRouter.post("/report/", dependencies=[Depends(get_current_user)])
async def report_user(report: ReportUserModel, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_phone = db.query(Contact.phone).filter(Contact.uuid == current_user).scalar()

        if report.phone == user_phone:
            raise HTTPException(status_code=400, detail="You cannot report yourself")

        with db.begin_nested():
            global_blacklist_entry = db.query(GlobalBlackList).filter(GlobalBlackList.phone == report.phone).first()
            if global_blacklist_entry:
                global_blacklist_entry.spam_reports += 1
                if global_blacklist_entry.spam_reports > 10:
                    global_blacklist_entry.spam = True
            else:
                global_blacklist_entry = GlobalBlackList(
                    phone=report.phone,
                    name=report.name,
                    spam_reports=1,
                    spam=False
                )
                db.add(global_blacklist_entry)

        user = db.query(Contact).filter(Contact.uuid == current_user).first()
        if user:
            reports_list = json.loads(user.reports_list) if user.reports_list else []

            reports_list.append({"phone": report.phone, "name": report.name})

            user.reports_list = json.dumps(reports_list)

            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "User reported successfully", "phone": report.phone, "name": report.name}



@dbRouter.post("/search/name/", dependencies=[Depends(get_current_user)])
async def search_user(search: SearchUserModel, db: Session = Depends(get_db)):
    try:
        results = db.query(GlobalBlackList).filter(GlobalBlackList.name.like(f"%{search.name}%")).all()
        if not results:
            raise HTTPException(status_code=404, detail="User not found")

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@dbRouter.post("/search/phone/", dependencies=[Depends(get_current_user)])
async def search_user_by_phone(search: SearchPhoneModel, db: Session = Depends(get_db)):
    try:
        if len(search.phone) <= 5:
            raise HTTPException(status_code=400, detail="Phone number length must be more than 5 characters")

        results = db.query(GlobalBlackList).filter(GlobalBlackList.phone.like(f"%{search.phone}%")).all()
        if not results:
            raise HTTPException(status_code=404, detail="User not found")

        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
