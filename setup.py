import setuptools

setuptools.setup(
    name="arggo",
    version="0.3.1",
    author="Miki Mendelson-Mints",
    author_email="mikimn1999@gmail.com",
    description="The no-brainer package for setting up python experiments.",
    url="https://github.com/mikimn/arggo",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["arggo-cli=arggo.cli:main"],
    },
    install_requires=[
        "setuptools",
    ],
    include_package_data=True,
    python_requires=">=3.7",
)
