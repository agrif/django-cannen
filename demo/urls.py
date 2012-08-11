from django.conf.urls.defaults import patterns, include, url

# django admin boilerplate
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # host cannen at /radio/
    url(r'^radio/', include('cannen.urls')),
    
    # optional (but helpful): add a login page
    url(r'^radio/login$', 'django.contrib.auth.views.login'),
    url(r'^radio/logout$', 'django.contrib.auth.views.logout_then_login'),

    # more django admin boilerplate
    url(r'^admin/', include(admin.site.urls)),
)
