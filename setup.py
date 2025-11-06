from setuptools import setup, find_packages

setup(
    name="jobqueue-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'jobqueue=jobqueue_cli.cli:cli',
        ],
    },
    author="Your Name",
    description="CLI-based background job queue system",
    python_requires=">=3.7",
)