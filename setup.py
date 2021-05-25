import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arc-cli",
    version="2.3.0",
    license="MIT",
    author="Sean Collings",
    author_email="sean@seanrcollings.com",
    description="A Regular CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/seanrcollings/arc/archive/v2.3.0tar.gz",
    url="https://github.com/seanrcollings/arc",
    keywords=["CLI", "extendable", "easy"],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={"arc": ["py.typed"]},
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)
