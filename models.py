from sqlalchemy import Column, String, Boolean, Integer
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class GlobalBlackList(Base):
    __tablename__ = 'globalBlackList'
    
    phone = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=True)
    spam = Column(Boolean, default=False)
    spam_reports = Column(Integer, default=0)


class Contact(Base):
    __tablename__ = 'contacts'
    
    uuid = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    contacts_list = Column(String, nullable=True)
    reports_list = Column(String, nullable=True)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)


    def generate_token(self):
        from jose import jwt
        from datetime import datetime, timedelta
        from config import SECRET_KEY, ALGORITHM

        now = datetime.now()
        expires = now + timedelta(minutes=30)

        token_payload = {
            "sub": self.uuid,
            "name": self.name,
            "exp": expires,
        }
        return jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)