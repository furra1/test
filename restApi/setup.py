from setuptools import setup, find_packages

setup(
    name = 'RestApi',
    description= 'RestApi для приложения',
    version= '1.0.0',
    author= 'preKolist_team',
    author_email='lolker5555@gmail.com',
    packages = find_packages(exclude = ['tests', 'test.*']),
    install_requires = [
        'aiohttp~=3.6.2',
        'aiohttp-apispec==2.2.3',
        'aiomisc~=9.6.11',
        'alembic~=1.3.3',
        'asyncpgsa==0.27.1',
        'ConfigArgParse~=1.0',
        'psycopg2-binary==2.8.4',
        'pytz==2019.3',
        'setproctitle==1.1.10',
    ],
    extras_require={
        'dev':[
            'coverage==5.0.3',
            'Faker==4.0.0',
            'locust',
            'pylama==7.7.1',
            'pytest~=5.3.5',
            'pytest-aiohttp~=0.3.0',
            'pytest-cov==2.8.1'
        ]
    },
    entry_points = {
        "console_scripts":[
            "restApi-server = restart.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "":['.txt', '*.ini'],
    },
    python_requires = ">=3.7",
)