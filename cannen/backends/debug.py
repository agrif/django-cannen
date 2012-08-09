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

from ..backend import CannenBackend, SongInfo
from django.core.files.storage import FileSystemStorage

class DebugBackend(CannenBackend):
    def __init__(self, out, delay):
        self.out = out
        self.delay = delay
        self.is_playing = False
        self.current = None
        self.next = []
    def play(self):
        self.is_playing = True
        self.out.write("player started\n")
    def stop(self):
        self.is_playing = False
        self.current = False
        self.next = []
        self.out.write("player stopped\n")
    def queue(self, url):
        self.out.write("queueing {0}\n".format(url));
        self.next.append(url)
        return True
    def run(self, on_next_song):
        import time
        while True:
            if not self.is_playing:
                on_next_song(None)
                time.sleep(self.delay)
                continue
            
            if self.next:
                self.current = self.next[0]
                self.next = self.next[1:]
                self.out.write("now playing {0}\n".format(self.current))
                on_next_song(self.current)
            else:
                self.current = None
                self.stop()
                on_next_song(None)
            time.sleep(self.delay)
    def get_info(self, model):
        return SongInfo(model, None, None, None, None)
    def get_storage(self):
        return FileSystemStorage()
    def register_uploaded(self, url):
        pass
    def unregister_uploaded(self, url):
        pass
