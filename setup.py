from setuptools import setup
from AllureReportLibrary.version import VERSION

setup(
    name='robotframework-allurereport',
    packages=['AllureReportLibrary'],
    version=VERSION,
    description='Allure Reporting Adaptor for Robot Framework',
    long_description=(
        'The Allure Adaptor for Robot Framework is a Library that can be'
        ' included in the Robot scripts to generate compatible XML files which'
        ' can then be used to generate the Allure HTML reports.'
    ),
    author='Eltjona Qato, Anne Kootstra',
    author_email='qatoeltjona@gmail.com, kootstra@hotmail.com',
    url='https://github.com/kootstra/robotframework-allurereport',
    keywords=['allure', 'robotframework', 'reporting'],
    license='MIT License',
    platforms='any',
    download_url=(
        'https://github.com/kootstra/robotframework-allurereport/tarball/1.1.1'
    ),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        "Development Status :: 4 - Beta"
    ],
    install_requires=[
        "lxml>=3.2.0",
        "namedlist",
        "py",
        "six>=1.9.0",
        "pytest-allure-adaptor>=1.7.6",
        "jprops>=1.0"
    ]
)
