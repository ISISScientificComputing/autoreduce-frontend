FROM autoreduction/base

# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
# also when updating the version here make sure it matches the one in setup.py
RUN python3 -m pip install --no-cache-dir gunicorn autoreduce-frontend==22.0.0.dev6

RUN useradd -m -s /bin/bash -u 1000 runner
USER runner
WORKDIR /home/runner

CMD autoreduce-webapp-manage collectstatic --no-input &&\
    gunicorn --workers 4 -b 0.0.0.0:8000 autoreduce_frontend.autoreduce_webapp.wsgi
