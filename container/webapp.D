FROM ghcr.io/autoreduction/base

# Installs frontend from your local repository
# Set version if you want to install from pypi
# add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple for packages in test.pypi.org
RUN python3 -m pip install --user --no-cache-dir gunicorn autoreduce-frontend/

# Add fixtures to the project for dev/debugging
ADD --chown=isisautoreduce:isisautoreduce autoreduce_frontend/autoreduce_webapp/fixtures/ fixtures/ 

USER root
RUN mkdir -p /var/www/api/
RUN chown isisautoreduce:isisautoreduce /var/www/api/
USER isisautoreduce

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "autoreduce_frontend.autoreduce_webapp.wsgi"]
