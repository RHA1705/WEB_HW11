import uvicorn
from fastapi import FastAPI

from src.routes.contacts import router

app = FastAPI()

app.include_router(router, prefix='/api')



@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000, reload=True)