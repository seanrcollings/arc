import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = os.getenv("VERSION")

if version is None:
    raise ValueError(
        "No Version specified. Either set the VERSION environment variable, or run the deploy script"
    )

setuptools.setup(
    name="arc-cli",
    version=version,
    license="MIT",
    author="Sean Collings",
    author_email="sean@seanrcollings.com",
    description="A Regular CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url=f"https://github.com/seanrcollings/arc/archive/v{version}.tar.gz",
    url="https://github.com/seanrcollings/arc",
    keywords=["CLI", "extendable", "easy"],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
