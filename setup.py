import setuptools

VERSION = "2.4.1"
DOWNLOAD = f"https://github.com/seanrcollings/arc/archive/v{VERSION}tar.gz"

with open("README.md", "r") as fh:
    LONG_DESC = fh.read()


setuptools.setup(
    name="arc-cli",
    version=VERSION,
    license="MIT",
    author="Sean Collings",
    author_email="sean@seanrcollings.com",
    description="A Regular CLI",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    download_url=DOWNLOAD,
    url="https://github.com/seanrcollings/arc",
    keywords=["CLI", "extendable", "easy", "arc"],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={"arc": ["py.typed"]},
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
)
