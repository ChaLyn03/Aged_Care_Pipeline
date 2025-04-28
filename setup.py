# setup.py
from setuptools import setup, find_packages

setup(
    name="aged_care_pipeline",
    version="0.1.0",
    packages=find_packages(),           # <-- this picks up scrapers/, parsers/, etc.
    install_requires=[
        "requests",
        "pandas",
        "APScheduler",
        "PyYAML",
        # …and any others you need
    ],
)
