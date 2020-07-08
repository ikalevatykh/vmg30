"""A setuptools based setup module."""

from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='vmg30',
    version='0.1.0',
    description='Client for VMG30 glove from Virtual Motion Lab',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ikalevatykh/vmg30',
    author='Igor Kalevatykh',
    author_email='kalevatykhia@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
    ],
    keywords='virtual reality glove VMG30',
    packages=find_packages(),
    install_requires=['numpy', 'pyserial', 'transforms3d'],
)
