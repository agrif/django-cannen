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

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('cannen.views',
    url(r'^add/url$', 'add_url'),
    url(r'^add/file$', 'add_file'),
    url(r'^delete/(\d+)$', 'delete'),
    url(r'move/(\d+)/([-+]?\d+)', 'move'),
    url(r'^play/(.*)$', 'play'),
    url(r'^library$', 'library'),
    url(r'^info$', 'info'),
    url(r'^$', 'index'),
)
