from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'stravagrab.views.index', name='index'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^stravaAuth/', 'stravagrab.views.stravaAuth', name='stravaAuth'),
    url(r'^authenticate/', 'stravagrab.views.authenticate', name='authenticate'),
    url(r'^selectStarredSegments/', 'stravagrab.views.selectStarredSegments', name='selectStarredSegments'),
    url(r'^segmentEffort/(?P<id>\d+)/', 'stravagrab.views.segmentEffort', name='segmentEffort'),
    # url(r'^stravaAuthenticated/', 'stravagrab.views.stravaAuthenticated', name='stravaAuthenticated'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_type=settings.MEDIA_ROOT)