import setuptools

with open("README.md" ,"r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="tame",
    version="0.0.2",
    url='https://github.com/meson800/tame',
    author="Christopher Johnstone",
    author_email="meson800@gmail.com",
    description="A minimal YAML-based metadata management system.",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["tame"],
    package_dir={'': 'src'},
    entry_points={
        "console_scripts": [
            "tame=tame.dispatch:dispatch_console"
            ]
        },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    install_requires=['PyYAML'],
    python_requires='>=3'
)
