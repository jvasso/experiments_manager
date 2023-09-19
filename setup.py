from setuptools import find_packages, setup

setup(
    name="experiments_manager",
    version="0.1",
    url="https://github.com/jvasso/experiments_manager",
    author="Jean Vassoyan",
    author_email="",

    package_dir={"": "src"},
    packages=find_packages(where="src"),

    install_requires=[
        "numpy>=1.19"
    ],
    python_requires=">=3.6"

)
