__author__ = 'jblowe'

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       # ex: /autosuggest?q=ASPARAG&elementID=ta.taxon
                       url(r'^', views.autosuggest, name='autosuggest'),
                       )