ch:
	sudo chmod 777 -R data/

up:
	docker-compose up --build

down:
	docker-compose down -v


kafka:
	docker-compose up -d zookeeper
	docker-compose up -d kafka
	docker-compose up -d kafkacat

pg:
	docker-compose up -d postgres

spark:
	docker-compose up -d spark

airflow:
	docker-compose up -d airflow

jupyter:
	docker-compose up -d jupyter
