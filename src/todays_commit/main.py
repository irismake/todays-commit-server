import logging

from fastapi import FastAPI
from starlette.responses import HTMLResponse

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from todays_commit.database import initialize_db
from todays_commit.database.connection import engine, SessionLocal

from todays_commit.routers import healthz, map, grass, place, token, oauth, user, location
# # 필요한 라우터들을 여기에 import 예: from todays_commit.routers import users, posts 등

logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    initialize_db()

# # 환경 변수에서 ORIGIN 설정
# origin = os.getenv("ORIGIN", "http://127.0.0.1:5173")
# origins = [origin]

# # CORS 미들웨어 추가
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 라우터 등록
app.include_router(healthz.router)
app.include_router(token.router)
app.include_router(oauth.router)
app.include_router(map.router)
app.include_router(grass.router)
app.include_router(place.router)
app.include_router(user.router)
app.include_router(location.router)
# app.include_router(users.router) 등 필요한 것 추가

# 홈 라우트
@app.get("/")
async def home():
    html = (
        '<a href="/docs">API 문서</a><br>'
    )
    return HTMLResponse(html)

@app.get("/test")
async def test_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}

# 개발용 실행 진입점
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=5999, reload=True)
