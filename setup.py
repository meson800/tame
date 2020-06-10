import setuptools
import sys

with open("README.md" ,"r", encoding='utf8') as fh:
    long_description = fh.read()

if sys.platform.startswith('win'):
    compile_args = ['-std:c++17']
else:
    # We need the c++fs library on linux
    compile_args = ['-std=c++17', '-lstdc++fs']
walk_module = setuptools.Extension('_tame_walk',
                         sources = ['src/_walk/main.cpp'],
                         extra_compile_args = compile_args)
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
    ext_modules = [walk_module],
    package_dir={'': 'src'},
    entry_points={
        "console_scripts": [
            "tame=tame.dispatch:dispatch_console"
            ],
        "gui_scripts": [
            "tamegui=tame.gui:main"
            ]
        },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    install_requires=[
        'PyYAML',
        'scandir;python_version<="3.4"',
        'colorama',
        'PyQt5',
        ],
    python_requires='>=3'
)
