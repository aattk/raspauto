from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='raspauto',
    version='0.1.6.9',
    description='Raspberry Automation Library and Voice Recognition',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='GNU',
    packages=find_packages(),
    author='Alpaslan Tetik',
    author_email='232arslan104@gmail.com',
    keywords=['raspberry', 'automotion','control'],
    url='https://github.com/aattk/raspauto',
    download_url='https://pypi.org/project/raspauto/',
    python_requires='>=3.6',
)

install_requires = [
    'python-telegram-bot'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)