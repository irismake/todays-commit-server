# 🛠️ Docker Compose 환경 제어
dc-up:
	docker compose -f docker-compose.yml up --build -d

dc-down:
	docker compose -f docker-compose.yml down

dc-down-v2:
	docker compose -f docker-compose.yml down --rmi all

# 🗄️ 데이터베이스 제어
db-create:
	docker compose -f docker-compose.yml exec postgres psql -p 5432 -U postgres -c "create database ggg"

db-recreate:
	docker compose -f docker-compose.yml stop -t 1 web
	docker compose -f docker-compose.yml exec postgres psql -p 5432 -U postgres -c "drop database ggg"
	docker compose -f docker-compose.yml exec postgres psql -p 5432 -U postgres -c "create database ggg"
	docker compose -f docker-compose.yml start web

# 🧬 Alembic 마이그레이션
db-update:
	docker compose -f docker-compose.yml exec web alembic upgrade head

db-schema-update:
	docker compose -f docker-compose.yml exec web alembic revision --autogenerate -m "schema-update"
