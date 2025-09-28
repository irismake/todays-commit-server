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
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
DB_NAME=...

# kakao
KAKAO_ADMIN_KEY=...
KAKAO_REST_API_KEY=...
KAKAO_JAVASCRIPT_KEY=...

# apple
APPLE_TEAM_ID=...
APPLE_CLIENT_ID=...
APPLE_KEY_ID=...
APPLE_REDIRECT_URI=...
APPLE_PRIVATE_KEY_FILE=...

# sk
SK_APP_KEY=...

# token
SECRET_KEY=...
TOKEN_ALGORITHM=...
```

### **Run (Docker)**
```bash
make dc-up         # docker compose up --build -d
make db-access     # 컨테이너 내부 postgres 접속(psql)
```

### **Run (수동)**
```bash
# 컨테이너 초기화
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker system prune

# 도커 빌드
docker compose build
# 도커 실행
docker compose up
# (옵션) 백그라운드에서 실행
docker compose up -d
```
* 중지/정리는 아래 Makefile Commands 참고

<br>

## **Makefile Commands**
### **Docker Compose 환경 제어**
```bash
make dc-up         # docker compose -f docker-compose.yml up --build -d
make dc-down       # docker compose -f docker-compose.yml down
make dc-down-v2    # docker compose -f docker-compose.yml down --rmi all   (이미지까지 정리)
```
### **데이터베이스 제어**
```bash
make db-access     # docker compose exec postgres psql -U postgres -d todays_commit
make db-create     # TodaysCommit DB 생성
make db-recreate   # 웹 일시 중지 → DB 드롭/재생성 → 웹 재시작
```

### **Alembic 마이그레이션**
```bash
make db-update         # alembic upgrade head
make db-schema-update  # alembic revision --autogenerate -m "schema-update"
```
&nbsp;

## **Migration(수동 실행 예시)**

### **Create & Apply**
```bash
docker compose exec web alembic revision --autogenerate -m "feat: add indices"
docker compose exec web alembic upgrade head
```


### **Downgrade**
```bash
docker compose exec web alembic downgrade -1
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

- `main` : 주요 개발 브랜치 
- `feature/*` : 기능 단위 브랜치  


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


## **Health Check**

- **/health** 엔드포인트: DB 연결 체크 후 200 반환

<br>

## **API specification**

[API Docs](https://wide-humor-7da.notion.site/API-21c4678d106480a69a57d4d9a6262a71)
