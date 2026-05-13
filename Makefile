COMPOSE = docker compose -f docker-compose.yaml

all:
	@$(COMPOSE) up -d --build

clean:
	@$(COMPOSE) down -v

fclean: clean
	@docker system prune -af

re: fclean all

.PHONY: all clean fclean re status logs