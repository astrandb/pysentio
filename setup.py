import setuptools
import codecs
import re
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^VERSION = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="pysentio",
    version=find_version('pysentio', 'const.py'),
    author="Ake Strandberg",
    author_email="ake@strandberg.eu",
    description="Python library for Sentio Pro Sauna Controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astrandb/pysentio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
        'Development Status :: 4 - Beta',
    ],
    python_requires='>=3.8',
    install_requires=["pyserial>=3.4"],
)
