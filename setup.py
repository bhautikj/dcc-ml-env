# setup.py
from setuptools import setup, find_packages

setup(
    name="dcc-ml-env",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dcc-ml-env=src.main:main',
        ],
    },
    install_requires=[
        # Add dependencies here
    ],
    author="DCC-Workon Team",
    author_email="team@dcc-workon.com",
    description="Creative work environment manager for small teams",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    #url="https://github.com/dcc-workon/dcc-workon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
)