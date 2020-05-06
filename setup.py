from setuptools import setup
setup(
    name='surveys2020',
    packages=["online_survey"],
    include_package_data=True,
    install_requires=[
	'gunicorn',
        'flask-sqlalchemy',
        'blinker==1.4',
        'click==7.1.1',
        'Flask==1.1.1',
        'Flask-DebugToolbar==0.11.0',
        'itsdangerous==1.1.0',
        'Jinja2==2.11.1',
        'MarkupSafe==1.1.1',
        'Werkzeug==1.0.0',
    ]
)
