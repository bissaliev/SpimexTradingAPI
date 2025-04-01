up:
	docker compose -f docker-compose.test.yml up --build -d
down:
	docker compose -f docker-compose.test.yml down -v
