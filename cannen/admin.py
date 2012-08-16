from models import SongFile
from models import UserSong
from models import GlobalSong
from django.contrib import admin

class SongFileAdmin(admin.ModelAdmin):
    fields = ['owner', 'file']
    list_filter = ['owner']

admin.site.register(SongFile, SongFileAdmin)
admin.site.register(UserSong)
admin.site.register(GlobalSong)
