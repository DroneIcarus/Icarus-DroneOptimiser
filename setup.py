from setuptools import setup, find_packages

setup(name='IcarUS',
      version='0.1',
      description='Scripts to optimize missions of QGroundControl',
      url='https://github.com/EskimoDesignLab',
      author='IcarUS',
      author_email='droneaquatique@groupes.usherbrooke.ca',
      license='',
      packages=find_packages(),
      include_package_data=True,
      test_suite='',
      tests_require=[],
      install_requires=['numpy',
                     'setuptools',
                     'opencv_python',
                     'matplotlib',
                     'networkx',
                     'requests'])