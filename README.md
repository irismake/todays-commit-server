# **todays-commit-server**

이 저장소는 FastAPI와 PostgreSQL로 구축하고 Docker Compose로 컨테이너화한 오늘의 커밋 (Today’s Commit) 백엔드를 포함합니다.
장소/커밋 데이터용 REST API, JWT 기반 인증(상위 레이어의 Apple/Kakao 소셜 로그인 연동), PNU/zone-code 매핑 서비스를 제공하며, 경량 배포 환경(예: Raspberry Pi + Nginx + Let’s Encrypt)에 최적화되어 있습니다.

<br>

## **How to Clone and Run**

### **Clone the Repository**
```bash
git clone https://github.com/todayscommit/todays-commit-server.git
cd todays-commit-server
```

### **Environment**
```bash
cp .env.example .env
# .env 파일에 데이터베이스/토큰/도메인 정보 설정
# POSTGRES_USER=...
# POSTGRES_PASSWORD=...
# POSTGRES_DB=...
# DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@db:5432/DBNAME
# JWT_SECRET=...
# APP_ENV=local|dev|prod
```

### **Run (Docker)**
```bash
docker compose up -d --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **Run (Local)**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

<br>

## **Migration**

### **Create & Apply (Alembic)**
```bash
# 변경사항 생성 (자동 감지)
alembic revision --autogenerate -m "feat: add commit indices"

# 업그레이드
alembic upgrade head

# 특정 버전으로 다운그레이드
alembic downgrade -1
```

### **Seed / Admin (옵션)**
```bash
python scripts/seed.py        # 초기 데이터 삽입
python scripts/create_admin.py # 관리자/테스트 계정 생성
```

<br>

## **File Structure**
```bash
.
├── app
│   ├── api                  # 라우터 (place, commit, auth 등)
│   ├── core                 # 설정, 보안(JWT), 의존성
│   ├── db                   # 세션/엔진, 초기화
│   ├── models               # SQLAlchemy 모델 (Place, Commit, Grass, User 등)
│   ├── schemas              # Pydantic 스키마
│   ├── services             # 비즈니스 로직 (PNU/zone 매핑, 거리 계산 등)
│   └── main.py              # FastAPI 엔트리포인트
├── alembic
│   ├── versions             # 마이그레이션 파일들
│   └── env.py
├── scripts                  # seed, admin 생성 등 유틸 스크립트
├── docker
│   ├── nginx.conf           # (옵션) 리버스 프록시 설정
│   └── Dockerfile           # API Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

<br>

## **Branching Strategy**

We use the **Git Flow** branching model:

- `main`: Contains the latest production-ready code. Updated only when the application is ready for deployment or an app update is scheduled.
- `dev`: Integration branch for ongoing development. All features/bugfixes merge here first.
- `feature/feature-name`: Feature branches created from `dev`. When completed, merge back into `dev`.
- **Deployment process**: Admin merges `dev` into `main` when the application is ready for production deployment/updates.

<br>

## **Commit Message Guidelines**

### **Commit format:**
```
[TYPE] : [Short description]

[Body] : [Notion Link and Task ID]
```

### **Types:**
- `feat`: A new feature  
- `fix`: A bug fix  
- `docs`: Documentation changes  
- `style`: Code style changes (formatting, missing semi-colons, etc.)  
- `refactor`: Code refactoring without adding new features or fixing bugs  
- `test`: Adding or updating tests  
- `chore`: Maintenance tasks  

<br>

## **Migration Guidelines**

### **Alembic file naming (recommended):**
```
[YYYYMMDD_HHMMSS]_[short_description].py
```
> 예: `20250928_143210_add_commit_index.py`

- 스키마 변경 전후로 로컬/테스트에서 `alembic upgrade head` 검증 필수  
- 인덱스/제약 조건 변경은 영향 범위(읽기/쓰기 경로)를 PR 본문에 명시

<br>

## **Health & Observability (Optional)**

- **/health** 엔드포인트: DB 연결 체크 후 200 반환  
- 로깅: 구조적 로그(JSON) 권장, `uvicorn` 로그 레벨 환경변수로 제어  
- (옵션) Sentry / Prometheus / Grafana 연동 가능

