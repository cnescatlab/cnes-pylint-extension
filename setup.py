import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cnes-pylint-extension",
    version="7.0.0rc1",
    author="CNES CatLab",
    description="A PyLint plugin to add CNES specific checks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cnescatlab/cnes-pylint-extension",
    packages=setuptools.find_packages(where='checkers'),
    package_dir={'': 'checkers'},
    license_file='LICENSE',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pylint-plugin-utils==0.7",
        "pylint>=3.0.0,<4.0.0"
    ],
    project_urls={
        'Bug Reports': 'https://github.com/cnescatlab/cnes-pylint-extension/issues'
    }
)
