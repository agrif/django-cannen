# first, get the project directory
# and a helper for constructing local paths
import os.path
project_dir = os.path.split(os.path.abspath(__file__))[0]
def project_path(p):
    return os.path.join(project_dir, p)

# tell python to load modules from ..
# in order to reach (uninstalled) cannen
import sys
sys.path.insert(0, project_path('..'))

#
# standard django boilerplate
#

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': project_path('demo.db'),
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

MEDIA_ROOT = project_path('media')
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'muxsr9ipwkw63duo_$jz=@w05z!hg#)u#(_2_#^&xs&fto8+s7'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'demo.urls'

TEMPLATE_DIRS = (
    project_path('templates'),
)

#
# added cannen to installed apps
#

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    
    'cannen',
)

#
# Cannen-specific settings
#

# using debug backend, instead of MPD
# for example only
#CANNEN_BACKEND = ('cannen.backends.mpd.MPDBackend', 'localhost', 6600, project_path('mpd/music'))
CANNEN_BACKEND = ('cannen.backends.debug.DebugBackend',)

# optional for cannen
CANNEN_TITLE = "Cannen Demo"
CANNEN_LISTEN_URLS = [
    ('MP3', '#mp3'),
    ('OGG', '#ogg'),
]

#
# Useful login stuff to support cannen
#

LOGIN_URL = "/radio/login"
LOGIN_REDIRECT_URL = "/radio/"
