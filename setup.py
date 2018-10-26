import setuptools
from uhost import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uhost",
    version=__version__,
    license='Apache 2.0',
    author="Connax OY",
    author_email="info@connax.io",
    description="Uhost library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/connax-utim/uhost-python",
    packages=setuptools.find_packages(exclude=['examples']),
    platforms='any',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'mysql-connector-python',
        'paho-mqtt',
        'pika',
        'six',
        'pycrypto',
    ],
)
