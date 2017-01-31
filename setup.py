from setuptools import setup

setup(
    name='keras_elastic_callback',
    version='0.1',
    description='Keras callbacks that sends all events and data to elasticsearch',
    url='http://github.com/aocenas/keras_elastic_callback',
    author='Andrej Ocenas',
    author_email='mr.ocenas@gmail.com',
    license='MIT',
    packages=['keras_elastic_callback'],
    install_requires=[
        'keras',
        'numpy',
        'elasticsearch',
    ],
    tests_require=[
        'pytest',
        'mock',
    ],
    keywords=['keras', 'elasticsearch', 'machine learning'],
    zip_safe=False
)
