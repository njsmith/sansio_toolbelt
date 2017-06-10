from setuptools import setup, find_packages

from sansio_toolbelt import __version__

setup(
    name='sansio_toolbelt',
    version=__version__,
    description="An efficient I/O buffer and other useful tools for implementing Sans-IO network protocols",
    long_description=open("README.rst").read(),
    author="Nathaniel J. Smith",
    author_email='njs@pobox.com',
    license="MIT",
    packages=find_packages(),
    url='https://github.com/njsmith/sansio_toolbelt',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Networking",
        ],
)
