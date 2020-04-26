from setuptools import setup, find_packages

setup(
    name='jamaica',
    version='0.0.1',
    description='Jamaica API',
    url='https://github.com/cohoe/jamaica',
    author='Grant Cohoe',
    packages=find_packages(),
    install_requires=['flask-restx', 'flask-cors', 'flask_sqlalchemy_session'],
)