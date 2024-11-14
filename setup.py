import setuptools
import subprocess
from glob import glob
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from games_nebula import __version__

subprocess.run(['bash', 'scripts/compile_mo_files.sh'])

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

locales = []
for l in os.listdir('./src/data/locale/'):
    locales.append((f'share/locale/{l}/LC_MESSAGES', glob(f'src/data/locale/{l}/LC_MESSAGES/*.mo')))
data_files = [
    #('share/applications', ['src/data/games_nebula.desktop']),
    ('share/icons', ['src/data/icons/games_nebula.png']),
    ('share/games_nebula/images', glob('src/data/images/*.png')),
    ('share/games_nebula/images/black', glob('src/data/images/black/*.png'))
]
data_files.extend(locales)

setuptools.setup(
    name="games_nebula",
    version=__version__,
    author="Ivan Yancharkin",
    author_email="yancharkin@gmail.com",
    description="Unofficial (Linux) client for GOG.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yancharkin/games_nebula",
    project_urls={
        "Bug Tracker": "https://github.com/yancharkin/games_nebula/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src", exclude=['bin', 'data']),
    scripts=['src/bin/games_nebula'],
    data_files=data_files,
    python_requires=">=3.6",
    install_requires=['PyQt6']
)
