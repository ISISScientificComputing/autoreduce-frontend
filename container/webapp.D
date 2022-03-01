FROM ghcr.io/autoreduction/base

# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
# also when updating the version here make sure it matches the one in setup.py
RUN python3 -m pip install --user --no-cache-dir gunicorn autoreduce-frontend==22.0.0.dev16

CMD autoreduce-webapp-manage collectstatic --no-input &&\
    gunicorn --workers 4 -b 0.0.0.0:8000 autoreduce_frontend.autoreduce_webapp.wsgi
