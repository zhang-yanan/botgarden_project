from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views

import landing

admin.autodiscover()

#
# Initialize our web site -things like our AuthN backend need to be initialized.
#
from main import cspace_django_site

cspace_django_site.initialize()

urlpatterns = patterns('',
                       #  Examples:
                       #  url(r'^$', 'cspace_django_site.views.home', name='home'),
                       #  url(r'^cspace_django_site/', include('cspace_django_site.foo.urls')),

                       #  Uncomment the admin/doc line below to enable admin documentation:
                       #  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', include('landing.urls', namespace='landing')),
                       url(r'^ireports/', include('ireports.urls')),
                       url(r'^autosuggest/', include('autosuggest.urls', namespace='autosuggest')),
                       url(r'^suggestpostgres/', include('suggestpostgres.urls', namespace='suggestpostgres')),
                       url(r'^suggestsolr/', include('suggestsolr.urls', namespace='suggestsolr')),
                       url(r'^suggest/', include('suggest.urls', namespace='suggest')),
                       url(r'^search/', include('search.urls')),
                       url(r'^service/', include('service.urls')),
                       url(r'^accounts/login/$', views.login, name='login'),
                       url(r'^accounts/logout/$', views.logout, name='logout'),
                       url(r'^landing/', include('landing.urls', namespace='landing')),
                       url(r'^imaginator/', include('imaginator.urls', namespace='imaginator')),
                       url(r'^internal/', include('internal.urls', namespace='internal')),
                       )
