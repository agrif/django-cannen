from setuptools import setup, find_packages

import cannen

setup(name='django-cannen',
      version=cannen.__version__,
      description='a django collaborative music frontend for MPD',
      author=cannen.__author__,
      author_email=cannen.__email__,
      license=cannen.__license__,
      url=cannen.__url__,
      
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      
      install_requires=['python-mpd>=0.3.0'])
