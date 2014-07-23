from distutils.core import setup

setup(
    name='Irkkaa Nörttien Kanssa',
    version='0.1.0',
    author='juke',
    author_email='virtanen@jukk.is',
    packages=['irckaaja', 'irckaaja.scripts'],
    scripts=['bin/irckaaja.py',],
    url='https://github.com/jukeks/IrkkaaNorttienKanssa',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
    install_requires=[
        "configobj >= 4.7.2",
    ],
)

