import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arc-cli",
    version="0.1.0",
    author="Sean Collings",
    author_email="sean@seanrcollings.com",
    description="A Regular CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanrcollings/cli",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)