# This file is part of Cannen, a collaborative music player.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
      
      install_requires=['python-mpd>=0.3.0'],
      extras_require={'FTP': ['pyftpdlib>=0.7.0']})
