import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arc-cli",
    version="0.8",
    license='MIT',
    author="Sean Collings",
    author_email="sean@seanrcollings.com",
    description="A Regular CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/seanrcollings/arc/archive/v0.5.1.tar.gz",
    url="https://github.com/seanrcollings/arc",
    keywords=['CLI', 'extendable', 'easy'],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)