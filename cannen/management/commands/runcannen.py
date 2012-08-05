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

from django.core.management.base import BaseCommand, CommandError
from cannen.models import UserSong, GlobalSong, User
import cannen.backend

class PlaylistManager(object):
    def __init__(self, out, backend):
        self.backend = backend
        self.out = out
    def on_next_song(self, now_playing):
        # clear out the old is_playing, if it exists
        GlobalSong.objects.filter(is_playing=True).delete()
        
        # update the current is_playing if there is a current
        current = None
        if now_playing:
            # set it up based on what our backend says
            current = GlobalSong.objects.filter(url=now_playing)[0]
            current.is_playing = True
            current.save()
            
        def add_queued():
            # figure out who has songs in the global list
            # and who has queued songs
            has_songs_listed = set([o.submitter.id for o in GlobalSong.objects.filter(is_playing=False)])
            has_songs_avail = set([o.owner.id for o in UserSong.objects.all()])
            
            need_to_add = has_songs_avail - has_songs_listed
            for uid in need_to_add:
                # find the one song to add
                to_add = UserSong.objects.filter(owner__id=uid)[0]
                global_to_add = GlobalSong.from_user_song(to_add)
                global_to_add.save()
                to_add.delete()
                
        # add some now
        add_queued()
        
        # update current is_playing if there is no current
        if not now_playing:
            # start mpd going with our queue
            try:
                current = GlobalSong.objects.all()[0]
                if not self.backend.queue(current.url):
                    current.delete()
                    return # try again with other things
                self.backend.play()
            except IndexError:
                # nothing to play :(
                pass
            # our queue + play call will result in another call to
            # on_next_song, so we'll resume there
            return
        
        # queue up the next song
        try:
            next_song = GlobalSong.objects.filter(is_playing=False)[0]
            if not self.backend.queue(next_song.url):
                next_song.delete()
                return # try again with others
        except IndexError:
            pass

def main(out):
    import settings
    backend = cannen.backend.get()
    backend.stop()
    
    manager = PlaylistManager(out, backend)
    manager.on_next_song(None)
    
    backend.run(manager.on_next_song)

class Command(BaseCommand):
    args = ''
    help = 'runs the cannen background playlist manager'
    
    def handle(self, *args, **options):
        main(self.stdout)
