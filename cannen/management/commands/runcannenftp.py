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
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import authenticate
from django.utils import autoreload

from pyftpdlib import ftpserver
from optparse import make_option
import errno
import StringIO
import os
import logging

import cannen
from cannen.models import UserSong, User, add_song_and_file

# helper to add to queue when file is closed
class FTPUploadedFile(StringIO.StringIO):
    def __init__(self, user, name):
        StringIO.StringIO.__init__(self)
        self.ftp_user = user
        self.ftp_name = name
        # to appease pyftpdlib, because StringIO does not have this attr
        # this shows up in the Handler as the file name
        self.name = self
    
    def close(self):
        pass # it will be closed by the handler!

# constructor for not permitted errors
def NotPermittedError(io=False):
    if io:
        return IOError(errno.EPERM, "Operation not permitted.")
    else:
        return OSError(errno.EPERM, "Operation not permitted.")

class CannenFilesystem(ftpserver.AbstractedFS):
    def __init__(self, root, cmd_channel):
        self.user = User.objects.all()[0]
        super(CannenFilesystem, self).__init__('/', cmd_channel)
    
    # all paths are the same
    def ftp2fs(self, ftppath):
        return ftppath
    def fs2ftp(self, fspath):
        return fspath
    def validpath(self, path):
        return True
    
    # helper to return a UserSong model from an FTP path
    def get_model(self, path):
        if len(path) <= 1:
            return None
        songs = UserSong.objects.exclude(file=None).filter(owner__id=self.user.id, url__endswith=path[1:])
        try:
            return songs[0]
        except IndexError:
            return None
        
    # the big one, oooooopeeeeeen fiiile!
    def open(self, filename, mode):
        # for some reason filename is *relative!!*
        # so no cutting off the /
        
        if '+' in mode or 'a' in mode:
            # we don't do read/write or append here. begone!
            raise NotPermittedError(True)
        
        if 'r' in mode:
            model = self.get_model(filename)
            if not model:
                raise NotPermittedError(True)
            model.file.file.open(mode)
            return model.file.file
        
        if 'w' in mode:
            return FTPUploadedFile(self.user, filename)
        
        raise NotPermittedError(True)
    
    # a bunch of useless things from os.*
    def mkdir(self, path):
        raise NotPermittedError()
    def chdir(self, path):
        raise NotPermittedError()
    def rmdir(self, path):
        raise NotPermittedError()
    def rename(self, src, dest):
        raise NotPermittedError()
    def chmod(self, path, mode):
        raise NotPermittedError()
    def readlink(self, path):
        raise NotPermittedError()
        
    # implementations of os.*
    def listdir(self, path):
        if path != '/':
            raise NotPermittedError()
        files = UserSong.objects.exclude(file=None).filter(owner__id=self.user.id)
        return [f.url.rsplit('/', 1)[1].encode("UTF-8") for f in files]
    def remove(self, path):
        model = self.get_model(path)
        if model:
            model.delete()
        else:
            raise OSError(errno.ENOENT, "No such file or directory.")
    def stat(self, path):
        model = self.get_model(path)
        if model:
            size = model.file.file.size
            return os.stat_result((0664, 0, 0, 0, 0, 0, size, 0, 0, 0))
        else:
            raise OSError(errno.ENOENT, "No such file or directory.")
    def lstat(self, path):
        return self.stat(path)
    
    # needed so that stat() isn't dumb
    def get_user_by_uid(self, uid):
        return self.cmd_channel.username
    def get_group_by_gid(self, gid):
        return self.cmd_channel.username
    
    # replacements for os.path.*
    def isfile(self, path):
        if len(path) >= 1:
            if path[1:] in self.listdir('/'):
                return True
        return False
    def islink(self, path):
        return False
    def isdir(self, path):
        return path == "/"
    def getsize(self, path):
        return 0
    def getmtime(self, path):
        return 0
    def realpath(self, path):
        return path
    def lexists(self, path):
        True
    
    # temp maker, not used here (though maybe it should be?)
    def mkstemp(self, suffix="", prefix="", dir=None, mode='wb'):
        raise NotPermittedError()

class CannenAuthorizer(ftpserver.DummyAuthorizer):
    def validate_authentication(self, username, password):
        if not authenticate(username=username, password=password):
            return False
        try:
            # add auth perms
            # l - list files
            # r - retrieve files
            # d - delete files
            # w - store files
            self.add_user(username, 'notthepassword', '.', perm='lrdw')
        except ftpserver.AuthorizerError:
            pass
        return True

class CannenHandler(ftpserver.FTPHandler):
    authorizer = CannenAuthorizer()
    abstracted_fs = CannenFilesystem
    banner = "cannen {0} mass uploader".format(cannen.__version__)
    
    def on_file_received(self, file):
        # add the model!
        data = file.getvalue()
        uploaded_file = SimpleUploadedFile(file.ftp_name, data, content_type=None)
        song, _ = add_song_and_file(file.ftp_user, uploaded_file)
        StringIO.StringIO.close(file)
        
    def on_incomplete_file_received(self, file):
        # do nothing!
        StringIO.StringIO.close(file)

def main(host, port):
    # create the server
    handler = CannenHandler
    server = ftpserver.FTPServer((host, port), handler)
    server.max_cons = 256
    server.max_cons_per_ip = 2
    server.serve_forever()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True, help='Tells Django to NOT use the auto-reloader.'),
    )
    args = '[optional port number, or ipaddr:port]'
    help = 'runs the cannen background ftp upload server'
    
    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError("Usage is runcannenftp {0}.".format(self.args))
        if len(args) == 0:
            host = ''
            port = 8021
        else:
            arg = args[0]
            try:
                if ':' in arg:
                    host, port = arg.rsplit(':', 1)
                    port = int(port)
                else:
                    host = ''
                    port = int(arg)
            except ValueError:
                raise CommandError("\"{0}\" is not a valid port number or address:port pair.".format(args[0]))
        
        use_reloader = options.get('use_reloader')
        if use_reloader:
            autoreload.main(main, (host, port))
        else:
            main(host, port)
