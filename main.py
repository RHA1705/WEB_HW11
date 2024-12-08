import uvicorn
from fastapi import FastAPI

from src.routes.contacts import router as contacts_router
from src.routes.users import router as users_router

app = FastAPI()

app.include_router(contacts_router, prefix='/api')
app.include_router(users_router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)