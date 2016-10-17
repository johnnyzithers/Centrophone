from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='centrophone',
    version='0.1.0',
    description='Centoroid organized sampler',
    author='Duncan MacConnell',
    author_email='duncanmacconnell@gmail.com',
    url='',
    long_description=long_description,
    keywords='csound centroid sampler',
    license='GPL',
    install_requires=[
        'numpy >= 1.10.1',
        'librosa >= 0.4.1'
    ]
)
