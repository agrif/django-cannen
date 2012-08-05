from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from urllib import unquote

import backend

# model for files uploaded
class SongFile(models.Model):
    owner = models.ForeignKey(User)
    file = models.FileField(upload_to="uploaded/", storage=backend.get().get_storage())
    
    def garbage_collect(self):
        if self.globalsong_set.count() > 0 or self.usersong_set.count() > 0:
            return
        # we're no longer needed, so delete!
        self.delete()

@receiver(post_save, sender=SongFile)
def register_uploaded(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        backend.get().register_uploaded(unquote(instance.file.url))

@receiver(pre_delete, sender=SongFile)
def unregister_uploaded(sender, **kwargs):
    instance = kwargs['instance']
    url = instance.file.url
    instance.file.delete(save=False)
    backend.get().unregister_uploaded(unquote(url))

# for user-local queues
class UserSong(models.Model):
    owner = models.ForeignKey(User)
    url = models.CharField(max_length=200)
    file = models.ForeignKey(SongFile, null=True, blank=True)
    
    def __unicode__(self):
        return self.url.rsplit('/')[-1]

@receiver(post_delete, sender=UserSong)
def user_song_delete(sender, **kwargs):
    instance = kwargs['instance']
    if instance.file:
        instance.file.garbage_collect()

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

@receiver(post_delete, sender=GlobalSong)
def global_song_delete(sender, **kwargs):
    instance = kwargs['instance']
    if instance.file:
        instance.file.garbage_collect()
