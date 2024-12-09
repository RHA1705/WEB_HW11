import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from src.routes.contacts import router as contacts_router
from src.routes.users import router as users_router
from src.conf.config import settings


app = FastAPI()

app.include_router(contacts_router, prefix='/api')
app.include_router(users_router, prefix='/api')


# @app.on_event("startup")
# async def startup():
#     # r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
#     #                       decode_responses=True)
#     await FastAPILimiter.init(r)
origins = [
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}


@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)
