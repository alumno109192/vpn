#!/usr/bin/env python3
"""
Setup script para VPN Manager
"""

from setuptools import setup, find_packages
from version import __version__, APP_NAME, APP_DESCRIPTION, APP_AUTHOR, APP_EMAIL

# Leer el README para la descripción larga
with open("README_CLEAN.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer los requisitos
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vpn-manager",
    version=__version__,
    author=APP_AUTHOR,
    author_email=APP_EMAIL,
    description=APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/vpn-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vpn-manager=Main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
    zip_safe=False,
)
