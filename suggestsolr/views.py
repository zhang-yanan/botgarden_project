__author__ = 'jblowe'

# suggest functionality for webapps that access solr
#
# does NOT use the Solr4 "suggest" facility.
#
# instead, it uses facet queries.
#
# this module is "plug-compatible" with the psql version
#
# invoke as:
#
# http://localhost:8000/suggest/?q=1-200&elementID=ob.objno1
#
# returns json like:
#
# [{"value": "1-200"}, {"value": "1-20000"}, {"value": "1-200000"}, ...  {"value": "1-200025"}, {"s": "object"}]


from django.http import HttpResponse
from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from search.appconfig import PARMS

import solr

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'suggestsolr')
SOLRSERVER = config.get('connect', 'SOLRSERVER')
SOLRCORE = config.get('connect', 'SOLRCORE')

# create a connection to a solr server
s = solr.SolrConnection(url='%s/%s' % (SOLRSERVER, SOLRCORE))

import sys, json, re
import cgi
import cgitb;

cgitb.enable()  # for troubleshooting


def solrtransaction(q, elementID):

    #elapsedtime = time.time()

    try:

        # do a search
        solrField = PARMS[elementID][3]
        querystring = '%s:%s*' % (solrField,q)
        print querystring
        response = s.query(querystring, facet='true', facet_field=[ solrField ], fq={},
                           rows=0, facet_limit=30,
                           facet_mincount=1)

        facets = response.facet_counts
        facets = facets['facet_fields']
        #_facets = {}
        result = []
        for key, values in facets.items():
            #_v = []
            for k, v in values.items():
                #_v.append((k, v))
                result.append({'value': k})
            #_facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)

        result.append({'s': solrField})

        return json.dumps(result)    # or "json.dump(result, sys.stdout)"

    except:
        sys.stderr.write("suggest solr query error!\n")
        return None

#@login_required()
def solrrequest(request):
    elementID = request.GET['elementID']
    q = request.GET['q']
    return HttpResponse(solrtransaction(q,elementID), mimetype='text/json')


