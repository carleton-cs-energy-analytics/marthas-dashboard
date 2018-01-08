from setuptools import setup

setup(
    name='marthas_dashboard',
    packages=['marthas_dashboard'],
    include_package_data=True,
    install_requires=[
        'flask',
        'bokeh'
    ],
)
