FROM autoreduction/base

ADD ./setup.py /autoreduce-frontend/setup.py

# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
# also when updating the version here make sure it matches the one in setup.py
RUN python3 -m pip install --no-cache-dir gunicorn autoreduce-frontend==22.0.0.dev5

CMD autoreduce-webapp-manage runserver 8000
