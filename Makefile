all: credentials migrate-with-fixtures

dev:
	python setup.py sdist bdist_wheel
	twine upload --repository testpypi dist/*

prod:
	python setup.py sdist bdist_wheel
	twine upload --repository pypi dist/*

credentials:
	autoreduce-creds-migrate

migrate:
	autoreduce-webapp-manage migrate

migrate-with-fixtures: migrate
	autoreduce-webapp-manage loaddata super_user_fixture status_fixture pr_test

selenium:
	docker run --network host --name selenium --rm -it -v /dev/shm:/dev/shm selenium/standalone-chrome:4.0.0-beta-3-prerelease-20210422
