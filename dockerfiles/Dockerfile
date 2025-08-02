# ARM 호환 Python 3.11 + Alpine
FROM --platform=linux/arm64 python:3.11-alpine

# 시스템 패키지 설치
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openblas-dev \
    lapack-dev \
    python3-dev \
    py3-numpy \
    py3-pandas \
    postgresql-dev \
    libpq \
    build-base

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# alembic config 복사
COPY ./alembic.ini ./
COPY ./alembic ./alembic
COPY ./src ./src/

ENV PYTHONPATH=./src

# 서버 실행
CMD ["uvicorn", "src.todays_commit.main:app", "--host", "0.0.0.0", "--port", "5999"]