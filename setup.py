from setuptools import find_packages
from distutils.core import setup

setup(
    name='spamurai',
    version='1.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "mako",
    ]
)
