all:
	python setup.py sdist bdist_wheel
	twine upload --repository testpypi dist/*

prod:
	python setup.py sdist bdist_wheel
	twine upload --repository pypi dist/*
