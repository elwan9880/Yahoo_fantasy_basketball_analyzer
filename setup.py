from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="yahoo_fantasy_basketball_analyzer",
    version="0.1.0",
    install_requires=requirements,
    author="Chun-Tse Shao, Frank Shih",
    author_email="elwan9880@gmail.com",
    packages=["yahoo_fantasy_basketball_analyzer"],
    python_requires=">=3"
)
