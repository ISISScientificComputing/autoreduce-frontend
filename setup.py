# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup, find_packages
from glob import glob
import os

PACKAGE_NAME = "autoreduce_frontend"

data_locations = [f"{PACKAGE_NAME}/templates/", f"{PACKAGE_NAME}/static/", f"{PACKAGE_NAME}/**/templates"]

data_files = []

for loc in data_locations:
    data_files.extend([f.split(f"{PACKAGE_NAME}/")[1] for f in glob(f"{loc}/**", recursive=True) if os.path.isfile(f)])
print(data_files)

setup(
    name=PACKAGE_NAME,
    version="22.0.0.dev21",  # when updating the version here make sure to also update webapp.D
    description="The frontend of the ISIS Autoreduction service",
    author="ISIS Autoreduction Team",
    url="https://github.com/autoreduction/autoreduce-frontend/",
    install_requires=[
        "autoreduce_qp==22.0.0.dev35", "Django==4.0.2", "django_extensions==3.1.5", "djangorestframework==3.13.1",
        "django-filter==21.1", "django-crispy-forms==1.14.0", "django-tables2==2.4.1", "requests==2.27.1",
        "httpagentparser==1.9.2"
    ],
    packages=find_packages(),
    package_data={"": data_files},
    entry_points={"console_scripts": ["autoreduce-webapp-manage = autoreduce_frontend.manage:main"]})
