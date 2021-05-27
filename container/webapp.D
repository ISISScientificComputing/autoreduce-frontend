FROM autoreduction/base

ADD ./setup.py /autoreduce-frontend/setup.py

# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
RUN python3 -m pip install --no-cache-dir gunicorn autoreduce-frontend==21.1.3

CMD autoreduce-webapp-manage runserver 8000
