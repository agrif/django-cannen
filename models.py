from django.db import models
from django.contrib.auth.models import User

import backend

# model for files uploaded
class SongFile(models.Model):
    owner = models.ForeignKey(User)
    file = models.FileField(upload_to="uploaded/", storage=backend.get().get_storage())

# for user-local queues
class UserSong(models.Model):
    owner = models.ForeignKey(User)
    url = models.CharField(max_length=200)
    file = models.ForeignKey(SongFile, null=True, blank=True)
    
    def __unicode__(self):
        return self.url.rsplit('/')[-1]

# for the global queue
class GlobalSong(models.Model):
    submitter = models.ForeignKey(User)
    url = models.CharField(max_length=200)
    file = models.ForeignKey(SongFile, null=True, blank=True)
    is_playing = models.BooleanField()
    
    def __unicode__(self):
        return self.url.rsplit('/')[-1]
    
    @classmethod
    def from_user_song(cls, user):
        return cls(submitter=user.owner, url=user.url, file=user.file, is_playing=False)
