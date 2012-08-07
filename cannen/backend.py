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

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
CANNEN_BACKEND = settings.CANNEN_BACKEND

def get():
    if type(CANNEN_BACKEND) == tuple:
        path = CANNEN_BACKEND[0]
        options = CANNEN_BACKEND[1:]
    else:
        path = CANNEN_BACKEND
        options = ()
    try:
        module, name = path.rsplit('.', 1)
        parts = path.split('.')
        module = __import__(module)
        cls = module
        for part in parts[1:]:
            cls = getattr(cls, part)
    except (AttributeError, ImportError, ValueError):
        raise ImproperlyConfigured("invalid cannen backend {0}".format(repr(CANNEN_BACKEND)))
    return cls(*options)

class SongInfo(object):
    def __init__(self, model, title, artist, album, time):
        self.title = title
        self.artist = artist
        self.album = album
        self.model = model
        self.time = time
        if not title:
            self.title = unicode(model)

class CannenBackend(object):
    # play the first song in the queue
    def play(self):
        raise NotImplementedError("CannenBackend.play")
    # stop playback and clear the queue / play state
    def stop(self):
        raise NotImplementedError("CannenBackend.stop")
    # add a url to the queue
    # return false if can't be done
    def queue(self, url):
        raise NotImplementedError("CannenBackend.queue")
    # while stopped, call on_next_song(None) periodically
    # while playing, call on_next_song(url) when a new song begins to play
    # this function can call play() and queue()
    def run(self, on_next_song):
        raise NotImplementedError("CannenBackend.run")
    # returns a SongInfo instance
    def get_info(self, model):
        raise NotImplementedError("CannenBackend.get_info")
    # returns a django Storage backend to use for uploaded files
    def get_storage(self):
        raise NotImplementedError("CannenBackend.get_storage")
    # called with uploaded file urls
    def register_uploaded(self, url):
        raise NotImplementedError("CannenBackend.register_uploaded")
    def unregister_uploaded(self, url):
        raise NotImplementedError("CannenBackend.unregister_uploaded")
