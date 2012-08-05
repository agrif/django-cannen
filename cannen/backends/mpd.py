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

# needed in order to import the mpd library
from __future__ import absolute_import

from ..backend import CannenBackend, SongInfo
from django.core.files.storage import FileSystemStorage

from select import select
import mpd

class MPDBackend(CannenBackend):
    def __init__(self, hostname, port, music_root):
        self.client = mpd.MPDClient()
        self.client.connect(host=hostname, port=port)
        self.last_song = None
        self.music_root = music_root
    def play(self):
        self.client.play()
    def stop(self):
        self.client.stop()
        self.client.clear()
        self.client.repeat(0)
        self.client.shuffle(0)
        self.client.consume(1)
        self.last_song = None
    def queue(self, url):
        try:
            self.client.add(url.encode('UTF-8'))
            return True
        except mpd.CommandError:
            return False
    def run(self, on_next_song):
        # keep track of our idle state and accumulated changes
        in_idle = False
        changed = []
        
        while True:
            # make sure to be in idle mode
            if not in_idle:
                self.client.send_idle()
                in_idle = True
            
            # check for events, but time out for checking database updates
            ready, _, _ = select([self.client], [], [], 1)
            
            # handle events
            if ready:
                changed += self.client.fetch_idle()
                self.client.send_idle()
                
                # reset our accumulated events here, unless it has player
                if not 'player' in changed:
                    changed = []
            
            # if we get a player event... update our state to reflect it
            if 'player' in changed:
                changed = []
                # turn off idle
                self.client.send_noidle()
                changed += self.client.fetch_idle()
                in_idle = False
                
                # get the current song, check against stored state
                # also get play state
                current_song = self.client.currentsong()
                playstate = self.client.status()['state']
                
                if not current_song or playstate == 'stop':
                    # playstate == 'stop' happens when the last queued
                    # song can't be played for some reason
                    if playstate == 'stop' and current_song:
                        self.client.deleteid(current_song['id'])
                    
                    current_song_key = None
                else:
                    current_song_key = current_song['id']
                
                # if it changed...
                if current_song_key != self.last_song:
                    # update our state, call on_next_song
                    self.last_song = current_song_key
                    if current_song_key:
                        on_next_song(current_song['file'])
                    else:
                        on_next_song(None)
                    # avoid double-calling on_next_song(None)
                    continue
            
            # if we're not playing anything...
            if self.last_song == None:
                # turn of idle, if needed
                if in_idle:
                    self.client.send_noidle()
                    changed += self.client.fetch_idle()
                    in_idle = False
                # and signal we're not playing
                on_next_song(None)
    def get_info(self, model):
        modeldat = None
        current = self.client.currentsong()
        if current and current['file'] == model.url:
            modeldat = current
        try:
            modeldat = self.client.listallinfo(model.url.encode('UTF-8'))[0]
        except (mpd.CommandError, IndexError):
            pass
        
        if modeldat:
            title = modeldat.get('title')
            artist = modeldat.get('artist')
            album = modeldat.get('album')
            return SongInfo(model, title, artist, album)
        else:
            return SongInfo(model, None, None, None)
    def get_storage(self):
        return FileSystemStorage(location=self.music_root, base_url="")
    def register_uploaded(self, url):
        self.client.update(url)
    def unregister_uploaded(self, url):
        self.client.update(url)
