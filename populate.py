from sqlalchemy import create_engine, Column, String, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'mysql+pymysql://sid:sample123@localhost:3306/spamCheck'

engine = create_engine(DATABASE_URI)
Base = declarative_base()

class GlobalBlackList(Base):
    __tablename__ = 'globalBlackList'
    
    phone = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=True)
    spam = Column(Boolean, default=False)
    spam_reports = Column(Integer, default=0)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

global_blacklist_entries = [
    {
        'phone': '9568523657',
        'name': 'Alice',
        'spam': False,
        'spam_reports': 0
    },
    {
        'phone': '8659635478',
        'name': 'Bob',
        'spam': False,
        'spam_reports': 0
    },
    {
        'phone': '8569321457',
        'name': 'Sheena Smith',
        'spam': True,
        'spam_reports': 12
    },
    {
        'phone': '8569321457',
        'name': 'Alan Walker',
        'spam': False,
        'spam_reports': 4
    },
    {
        'phone': '8569321457',
        'name': 'Ricko Rodrigo',
        'spam': False,
        'spam_reports': 8
    },
]

for entry in global_blacklist_entries:
    global_blacklist = GlobalBlackList(**entry)
    session.add(global_blacklist)

session.commit()

session.close()

print("Database populated successfully!")

