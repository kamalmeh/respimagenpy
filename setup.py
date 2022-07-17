from setuptools import setup, find_packages


setup(
    name="respimagenpy",
    version='0.1.0',
    description='Generate set of responsive images for supplied images',
    author='Kamal Mehta',
    author_email='kamal.h.mehta@smiansh.com',
    url='https://www.smiansh.com',
    license='MIT',
    install_requires=[
        'pillow'
    ],
    packages=find_packages(),
    zip_safe=False
)