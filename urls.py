from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('cannen.views',
    url(r'^add/url$', 'add_url'),
    url(r'^add/file$', 'add_file'),
    url(r'^delete/(\d+)$', 'delete'),
    url(r'^info$', 'info'),
    url(r'^$', 'index'),
)
