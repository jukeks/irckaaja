from setuptools import setup

setup(
    name="irckaaja",
    version="0.1.0",
    author="juke",
    author_email="virtanen@jukk.is",
    packages=["irckaaja", "irckaaja.scripts"],
    url="https://github.com/jukeks/IrkkaaNorttienKanssa",
    license="LICENSE.txt",
    description="Event based IRC bot.",
    install_requires=[
        "configobj >= 4.7.2",
    ],
    entry_points={
        "console_scripts": [
            "irckaaja = irckaaja.irckaaja:main",
        ]
    },
)
