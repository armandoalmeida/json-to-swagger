import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="json-to-swagger",
    version="0.0.5",
    author="Jose Armando Almeida Neto",
    author_email="jose@armandoalmeida.com.br",
    description="Python utility created to convert JSON to Swagger definitions structure, based on entities concept.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/armandoalmeida/json-to-swagger",
    packages=setuptools.find_packages(),
    install_requires=[
        "swagger-parser", "pyyaml", "inflect"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)