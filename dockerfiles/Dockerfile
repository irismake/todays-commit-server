# ARM 호환 Python 3.11 기반 슬림 이미지
FROM --platform=linux/arm64 python:3.11-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    python3-numpy \
    python3-pandas \
    libopenblas-dev \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-deps

# 프로젝트 전체 복사
COPY . .

# 서버 실행
CMD ["python", "src/ggg/app.py"]
