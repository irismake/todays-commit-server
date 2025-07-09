import logging

from fastapi import FastAPI
from starlette.responses import HTMLResponse

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from ggg.database.connection import engine, SessionLocal

from ggg.routers import healthz 
# # 필요한 라우터들을 여기에 import 예: from ggg.routers import users, posts 등

logger = logging.getLogger(__name__)

app = FastAPI()

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

    uvicorn.run("main:app", port=5000, reload=True)
