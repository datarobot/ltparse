from setuptools import setup


requirements = [
        'pyYAML',
        'click',
        'trafaret'
        ]

test_requirements = [
    'pytest'
    ]

setup_requirements = [
    'pytest-runner',
    'setuptools-pep8'
    ]

setup(name='layout_parser',
      version='0.0.1',
      packages=['ltparse'],
      install_requires=requirements,
      test_suite='tests',
      tests_require=test_requirements,
      setup_requires=setup_requirements,
      entry_points={
          'console_scripts': [
              'ltparse = ltparse.cli:cli'
              ]
          }
      )
