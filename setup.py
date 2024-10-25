from setuptools import setup

setup(
    name='tinyODM',
    version='0.1.0',    
    description='A very simple ODM for tinyDB',
    url='https://github.com/zenAurelius/tinyODM',
    author='zenAurelius',
    license='MIT',
    packages=['tinyODM'],
    install_requires=['tinydb',
                      'tinydb-serializer'                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.7',
    ],
)
