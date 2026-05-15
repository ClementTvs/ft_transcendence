COMPOSE = docker compose

all:
	$(COMPOSE) up --build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

seed:
	$(COMPOSE) exec backend python seed_db.py

clean:
	@$(COMPOSE) down -v

fclean: clean
	@docker system prune -af

re: fclean all

.PHONY: all up down seed clean fclean re