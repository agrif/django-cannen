from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ValidationError
from django.template import RequestContext

from django.conf import settings
CANNEN_BACKEND = settings.CANNEN_BACKEND

from models import UserSong, GlobalSong, SongFile

@login_required
def index(request):
    return render_to_response('cannen/index.html', {},
                              context_instance=RequestContext(request))

@login_required
def info(request):
    try:
        now_playing = GlobalSong.objects.filter(is_playing=True)[0]
        now_playing = CANNEN_BACKEND.get_info(now_playing)
    except IndexError:
        now_playing = None
    playlist = GlobalSong.objects.filter(is_playing=False)
    userqueue = UserSong.objects.filter(owner=request.user)
    playlist = [CANNEN_BACKEND.get_info(m) for m in playlist]
    userqueue = [CANNEN_BACKEND.get_info(m) for m in userqueue]

    data = dict(current=now_playing, playlist=playlist, queue=userqueue)
    return render_to_response('cannen/info.html', data,
                              context_instance=RequestContext(request))

@login_required
def delete(request, songid):
    song = get_object_or_404(UserSong, pk=songid)
    if song.owner.id != request.user.id:
        raise PermissionDenied()
    song.delete()
    return HttpResponseRedirect(reverse('cannen.views.index'))

@login_required
def add_url(request):
    url = request.POST['url']
    if url == '':
        raise ValidationError("url must not be empty")
    UserSong(owner=request.user, url=url).save()
    return HttpResponseRedirect(reverse('cannen.views.index'))

@login_required
def add_file(request):
    newfile = SongFile(owner=request.user, file=request.FILES['file'])
    newfile.save()
    newsong = UserSong(owner=newfile.owner, url=newfile.file.url, file=newfile)
    newsong.save()
    CANNEN_BACKEND.register_uploaded(newsong.url)
    return HttpResponseRedirect(reverse('cannen.views.index'))
