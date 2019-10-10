from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

VERSION = 0.1

setup(
    name='Yahoo Fantasy Basketball Analyzer',
    version=VERSION,
    install_requires=requirements,
    author='Chun-Tse Shao, Frank Shih',
    author_email='elwan9880@gmail.com'
)
