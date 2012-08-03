from select import select
import mpd

class SongInfo(object):
    def __init__(self, model, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album
        self.model = model
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
        return SongInfo(model, None, None, None)
    def get_storage(self):
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()
    def register_uploaded(self, url):
        pass

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
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage(location=self.music_root, base_url="")
    def register_uploaded(self, url):
        self.client.update(url)
