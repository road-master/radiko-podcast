#!/usr/bin/env python
"""The setup script."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    author="Master",
    author_email="roadmasternavi@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: System",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Filesystems",
        "Typing :: Typed",
    ],
    dependency_links=[],
    description="Automatic archiver for radiko program which queried by YAML file.",  # noqa: E501 pylint: disable=line-too-long
    entry_points={"console_scripts": ["radiko-podcast=radikopodcast.cli:radiko_podcast"]},
    exclude_package_data={"": ["__pycache__", "*.py[co]", ".pytest_cache"]},
    include_package_data=True,
    install_requires=[
        "click",
        "errorcollector",
        "ffmpeg-python",
        "radikoplaylist",
        "yamldataclassconfig",
        "sqlalchemy",
        "inflector",
        "asynccpu",
        "asyncffmpeg",
    ],
    keywords="radikopodcast",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="radikopodcast",
    packages=find_packages(
        include=["radikopodcast", "radikopodcast.*", "tests", "tests.*"]
    ),  # noqa: E501 pylint: disable=line-too-long
    package_data={"radikopodcast": ["py.typed"], "tests": ["*"]},
    python_requires=">=3.9",
    url="https://github.com/road-master/radiko-podcast",
    version="1.0.1",
    zip_safe=False,
)
