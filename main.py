from fastapi import FastAPI
from routers.db.dbops import dbRouter
from routers.user.users import userRouter
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(dbRouter)
app.include_router(userRouter)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
