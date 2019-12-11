from setuptools import setup

setup(
    name='xmas',
    version='0.1',
    py_modules=['xmas'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        xmas=xmas:cli
    ''',
)


'''
$ pyenv virtualenv venv
$ . venv/bin/activate
$ pip install --editable .

$ xmas
'''