COMPOSE = docker compose

all:
	$(COMPOSE) up --build

clean:
	@$(COMPOSE) down -v

fclean: clean
	@docker system prune -af

re: fclean all

.PHONY: all clean fclean re