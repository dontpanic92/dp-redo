import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dp-redo",
    version="3.0.1",
    author="Shengqiu Li",
    author_email="lishengqiu.hit@gmail.com",
    description="A python variant of the redo build system, with which You Can (Not) Redo.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dontpanic92/dp-redo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)