from distutils.core import setup
from setuptools import find_packages

description = """
Python package to build and manipulate temporal NetworkX graphs.
"""

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open(f"src/networkx_temporal/__version__.py") as f:
    version = f.read().split()[-1].strip('"')

setup(
    name="networkx-temporal",
    version=version.strip(),
    description=description.strip(),
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nelsonaloysio/networkx-temporal",
    author="Nelson Aloysio Reis de Almeida Passos",
    license="MIT",
    keywords=["Network", "Graph", "Dynamic Network", "Temporal Graph"],
    python_requires=">=3.7",
    package_dir={"": "src"},
    # py_modules=["networkx_temporal.networkx_temporal"],
    packages=find_packages(
        where="src",
        exclude=["build.*", "test.*"]
    ),
    project_urls={
        "Source": "https://github.com/nelsonaloysio/networkx-temporal",
        "Tracker": "https://github.com/nelsonaloysio/networkx-temporal/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
