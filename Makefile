# pipeline com alvos encadeados


PSQL=psql "postgresql+psycopg2://{user[postgres]}:{config['password']}@{config['host']}:{config['port']}/{config['database']}

init:
	$(PSQL) -f sql/00_schema_types.sql

ddl:
	$(PSQL) -f sql/01_ddl.sql

seed:
	$(PSQL) -f sql/02_dml_seed.sql

checks:
	$(PSQL) -f sql/03_checks.sql

queries_dicts:
	python3 python/run_queries_dicts.py

queries_lists:
	python3 python/run_queries_lists.py

upsert:
	python3 python/upsert.py

delete:
	python3 python/delete_mass.py

report:
	python3 python/report.py

all: init ddl seed checks queries_dicts queries_lists upsert delete report