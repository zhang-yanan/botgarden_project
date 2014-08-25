import re
import time, datetime
import csv
import solr
import cgi
import logging
from os import path

from django.http import HttpResponse, HttpResponseRedirect
from cspace_django_site.main import cspace_django_site

# global variables

from appconfig import MAXMARKERS, MAXRESULTS, MAXLONGRESULTS, MAXFACETS, IMAGESERVER, BMAPPERSERVER, BMAPPERDIR, TITLE
from appconfig import BMAPPERCONFIGFILE, SOLRSERVER, SOLRCORE, LOCALDIR, DROPDOWNS, SEARCH_QUALIFIERS, PARMS, FIELDS
from appconfig import LOCATION, EMAILABLEURL, SUGGESTIONS, LAYOUT, CSPACESERVER, INSTITUTION

SolrIsUp = True # an initial guess! this is verified below...
FACETS = {}

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('portal startup', '-', '%s | %s | %s' % (SOLRSERVER, IMAGESERVER, BMAPPERSERVER)))

def loginfo(infotype, context, request):
    logdata = ''
    #user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    if 'count' in context:
        count = context['count']
    else:
        count = '-'
    if 'querystring' in context:
        logdata = context['querystring']
    if 'url' in context:
        logdata += ' :: %s' % context['url']
    logger.info('%s :: %s :: %s :: %s' % (infotype, count, username, logdata))


def getfromXML(element,xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*\)'(.*)'$", "\\1", result)
    return result


def deURN(urn):
    #find identifier in URN
    m = re.search("\'(.*)\'$", urn)
    if m is not None:
        # strip out single quotes
        return m.group(0)[1:len(m.group(0)) - 1]


def getfields(fieldset):
    # for solr faceting
    if fieldset == 'inCSV':
        pickField = 'name'
    elif fieldset == 'Facet':
        pickField = 'solrfield'
    elif fieldset == 'FacetLabels':
        pickField = 'label'
        fieldset = 'Facet'
    else:
        pickField = 'solrfield'

    return [ f[pickField] for f in FIELDS[fieldset] ]


def getfacets(response):
    #facets = response.get('facet_counts').get('facet_fields')
    facets = response.facet_counts
    facets = facets['facet_fields']
    _facets = {}
    for key, values in facets.items():
        _v = []
        for k, v in values.items():
            _v.append((k, v))
        _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
    return _facets


def parseTerm(queryterm):
    queryterm = queryterm.strip(' ')
    terms = queryterm.split(' ')
    terms = ['"' + t + '"' for t in terms]
    result = ' AND '.join(terms)
    if 'AND' in result: result = '(' + result + ')' # we only need to wrap the query if it has multiple terms
    return result


def makeMarker(location):
    if location:
        return location.replace(' ','')
    else:
        return None


def writeCsv(filehandle, items, writeheader):
    fieldset = getfields('inCSV')
    writer = csv.writer(filehandle, delimiter='\t')
    # write the berkeley mapper header as the header for the csv file, if asked...
    if writeheader:
        writer.writerow(getfields('bMapper'))
    for item in items:
        # get the cells from the item dict in the order specified; make empty cells if key is not found.
        row = []
        for x in item['otherfields']:
            cell = x['value']
            # the following few lines are a hack to handle non-unicode data which appears to be present in the solr datasource
            if isinstance(cell, unicode):
                try:
                    cell = cell.translate({0xd7: u"x"})
                    cell = cell.decode('utf-8', 'ignore').encode('utf-8')
                    #cell = cell.decode('utf-8','ignore').encode('utf-8')
                    #cell = cell.decode('utf-8').encode('utf-8')
                except:
                    print 'unicode problem', cell.encode('utf-8', 'ignore')
                    cell = u'invalid unicode data'
            row.append(cell)
        writer.writerow(row)


def setupGoogleMap(requestObject, context):
    selected = []
    for p in requestObject:
        if 'item-' in p:
            selected.append(requestObject[p])
    mappableitems = []
    markerlist = []
    for item in context['items']:
        if item['csid'] in selected:
            m = makeMarker(item['location'])
            if len(mappableitems) >= MAXMARKERS: break
            if m is not None:
                #print 'm= x%sx' % m
                markerlist.append(m)
                mappableitems.append(item)
    context['mapmsg'] = []
    if len(context['items']) < context['count']:
        context['mapmsg'].append('%s points plotted. %s selected objects examined (of %s in result set).' % (
            len(markerlist), len(selected), context['count']))
    else:
        context['mapmsg'].append(
            '%s points plotted. all %s selected objects in result set examined.' % (len(markerlist), len(selected)))
    context['items'] = mappableitems
    context['markerlist'] = '&markers='.join(markerlist[:MAXMARKERS])
    if len(markerlist) >= MAXMARKERS:
        context['mapmsg'].append(
            '%s points is the limit. Only first %s accessions (with latlongs) plotted!' % (MAXMARKERS, len(markerlist)))
    return context


def setupBMapper(requestObject, context):
    context['berkeleymapper'] = 'set'
    selected = []
    for p in requestObject:
        if 'item-' in p:
            selected.append(requestObject[p])
    mappableitems = []
    for item in context['items']:
        if item['csid'] in selected:
            m = makeMarker(item['location'])
            if m is not None:
                mappableitems.append(item)
    context['mapmsg'] = []
    filename = 'bmapper%s.csv' % datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    #filehandle = open(filename, 'wb')
    filehandle = open(path.join(LOCALDIR, filename), 'wb')
    writeCsv(filehandle, mappableitems, writeheader=False)
    filehandle.close()
    context['mapmsg'].append('%s points of the %s selected objects examined had latlongs (%s in result set).' % (
        len(mappableitems), len(selected), context['count']))
    #context['mapmsg'].append('if our connection to berkeley mapper were working, you be able see them plotted there.')
    context['items'] = mappableitems
    bmapperconfigfile = '%s/%s/%s' % (BMAPPERSERVER, BMAPPERDIR, BMAPPERCONFIGFILE)
    tabfile = '%s/%s/%s' % (BMAPPERSERVER, BMAPPERDIR, filename)
    context[
        'bmapperurl'] = "http://berkeleymapper.berkeley.edu/run.php?ViewResults=tab&tabfile=%s&configfile=%s&sourcename=Consortium+of+California+Herbaria+result+set&maptype=Terrain" % (
        tabfile, bmapperconfigfile)
    return context
    # return HttpResponseRedirect(context['bmapperurl'])


def setDisplayType(requestObject):
    if 'displayType' in requestObject:
        displayType = requestObject['displayType']
    elif 'search-list' in requestObject:
        displayType = 'list'
    elif 'search-full' in requestObject:
        displayType = 'full'
    elif 'search-grid' in requestObject:
        displayType = 'grid'
    else:
        displayType = 'list'

    return displayType

def extractValue(listItem,key):
    # make all arrays into strings for display
    if key in listItem:
        if type(listItem[key]) == type([]):
            temp = ', '.join(listItem[key])
        else:
            temp = listItem[key]
    else:
        temp = ''

    # handle dates (convert them to collatable strings)
    if isinstance(temp, datetime.date):
        try:
            #item[p] = item[p].toordinal()
            temp = temp.isoformat().replace('T00:00:00+00:00', '')
        except:
            print 'date problem: ', temp

    return temp


def setConstants(context):
    if not SolrIsUp: context['errormsg'] = 'Solr is down!'
    context['suggestsource'] = SUGGESTIONS
    context['title'] = TITLE
    context['imageserver'] = IMAGESERVER
    context['cspaceserver'] = CSPACESERVER
    context['institution'] = INSTITUTION
    context['emailableurl'] = EMAILABLEURL
    context['dropdowns'] = FACETS
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    context['qualifiers'] = SEARCH_QUALIFIERS
    context['resultoptions'] = [100, 500, 1000, 2000]

    context['displayTypes'] = (
        ('list', 'List'),
        ('full', 'Full'),
        ('grid', 'Grid'),
    )

    # copy over form values to context if they exist
    try:
        requestObject = context['searchValues']

        context['displayType'] = setDisplayType(requestObject)
        if 'url' in requestObject: context['url'] = requestObject['url']
        if 'querystring' in requestObject: context['querystring'] = requestObject['querystring']
        if 'core' in requestObject: context['core'] = requestObject['core']
        if 'maxresults' in requestObject: context['maxresults'] = int(requestObject['maxresults'])

        if 'maxfacets' in requestObject:
            context['maxfacets'] = int(requestObject['maxfacets'])
        else:
            context['maxfacets'] = MAXFACETS

    except:
        print "no searchValues set"
        context['displayType'] = setDisplayType({})
        context['url'] = ''
        context['querystring'] = ''
        context['core'] = SOLRCORE
        context['maxresults'] = MAXRESULTS


    context['PARMS'] = PARMS
    context['FIELDS'] = FIELDS

    return context


def doSearch(solr_server, solr_core, context):
    elapsedtime = time.time()
    context = setConstants(context)
    requestObject = context['searchValues']

    # create a connection to a solr server
    s = solr.SolrConnection(url='%s/%s' % (solr_server, solr_core))
    queryterms = []
    urlterms = []
    facetfields = getfields('Facet')
    if 'map-google' in requestObject or 'csv' in requestObject or 'map-bmapper' in requestObject:
        querystring = requestObject['querystring']
        url = requestObject['url']
        context['maxresults'] = MAXRESULTS
    else:
        for p in requestObject:
            if p in ['csrfmiddlewaretoken', 'displayType', 'resultsOnly', 'maxresults', 'url', 'querystring', 'pane',
                     'pixonly', 'locsonly', 'acceptterms']: continue
            if '_qualifier' in p: continue
            if 'select-' in p: continue # skip select control for map markers
            if not p in requestObject: continue
            if not requestObject[p]: continue
            if 'item-' in p: continue
            searchTerm = requestObject[p]
            terms = searchTerm.split(' OR ')
            ORs = []
            for t in terms:
                t = t.strip()
                if t == 'Null':
                    t = '[* TO *]'
                    index = '-' + PARMS[p][3]
                else:
                    if p in DROPDOWNS:
                        # if it's a value in a dropdown, it must always be an "exact search"
                        t = '"' + t + '"'
                        index = PARMS[p][3].replace('_txt', '_s')
                    elif p + '_qualifier' in requestObject:
                        # print 'qualifier:',requestObject[p+'_qualifier']
                        qualifier = requestObject[p + '_qualifier']
                        if qualifier == 'exact':
                            index = PARMS[p][3].replace('_txt', '_s')
                            t = '"' + t + '"'
                        elif qualifier == 'phrase':
                            index = PARMS[p][3]
                            t = '"' + t + '"'
                        elif qualifier == 'keyword':
                            t = t.split(' ')
                            t = ' +'.join(t)
                            t = '(+' + t + ')'
                            t = t.replace('+-', '-') # remove the plus if user entered a minus
                            index = PARMS[p][3].replace('_ss', '_txt')
                            index = index.replace('_s', '_txt')
                    else:
                        t = t.split(' ')
                        t = ' +'.join(t)
                        t = '(+' + t + ')'
                        t = t.replace('+-', '-') # remove the plus if user entered a minus
                        index = PARMS[p][3]
                if t == 'OR': t = '"OR"'
                if t == 'AND': t = '"AND"'
                ORs.append('%s:%s' % (index, t))
            searchTerm = ' OR '.join(ORs)
            if ' ' in searchTerm and not '[* TO *]' in searchTerm: searchTerm = ' (' + searchTerm + ') '
            queryterms.append(searchTerm)
            urlterms.append('%s=%s' % (p, cgi.escape(requestObject[p])))
        querystring = ' AND '.join(queryterms)
        print querystring

        if urlterms != []:
            urlterms.append('displayType=%s' % context['displayType'])
            urlterms.append('maxresults=%s' % requestObject['maxresults'])
        url = '&'.join(urlterms)

    try:
        pixonly = requestObject['pixonly']
        querystring += " AND %s:[* TO *]" % PARMS['blobs'][3]
        url += '&pixonly=True'
    except:
        pixonly = None

    try:
        locsonly = requestObject['locsonly']
        querystring += " AND %s:[-90,-180 TO 90,180]" % LOCATION
        url += '&locsonly=True'
    except:
        locsonly = None

    try:
        response = s.query(querystring, facet='true', facet_field=facetfields, fq={},
                           rows=context['maxresults'], facet_limit=MAXFACETS,
                           facet_mincount=1)
    except:
        #raise
        context['errormsg'] = 'Solr4 query failed'
        return context

    facets = getfacets(response)
    results = response.results

    context['items'] = []
    imageCount = 0
    displayFields = context['displayType'] + 'Display'
    for i, listItem in enumerate(results):
        item = {}
        item['counter'] = i
        otherfields = []

        # pull out the fields that have special functions in the UI
        for p in PARMS:
            if 'mainentry' in PARMS[p][1]:
                item['mainentry'] = extractValue(listItem,PARMS[p][3])
            elif 'accession' in PARMS[p][1]:
                x = PARMS[p]
                item['accession'] = extractValue(listItem,PARMS[p][3])
                item['accessionfield'] = PARMS[p][4]

        for p in FIELDS[displayFields]:
            try:
                otherfields.append({'label':p['label'],'name':p['name'],'value': extractValue(listItem,p['solrfield'])})

            except:
                pass
                #raise
                #otherfields.append({'label':p['label'],'value': ''})
        item['otherfields'] = otherfields
        if 'csid_s' in listItem.keys():
            item['csid'] = listItem['csid_s']
        # the list of blob csids need to remain an array, so restore it from psql result
        if 'blob_ss' in listItem.keys():
            item['blobs'] = listItem['blob_ss']
            imageCount += len(item['blobs'])
        if LOCATION in  listItem.keys():
            item['marker'] = makeMarker(listItem[LOCATION])
            item['location'] = listItem[LOCATION]
        context['items'].append(item)

    if context['displayType'] in ['full', 'grid'] and response._numFound > MAXLONGRESULTS:
        context['recordlimit'] = '(limited to %s for long display)' % MAXLONGRESULTS
        context['items'] = context['items'][:MAXLONGRESULTS]
    if context['displayType'] == 'list' and response._numFound > context['maxresults']:
        context['recordlimit'] = '(display limited to %s)' % context['maxresults']

    #print 'items',len(context['items'])
    context['count'] = response._numFound
    context['labels'] = []
    context['fields'] = []

    m = {}
    #for p in FIELDS[displayFields]:
    #    context['labels'].append(p['label'])
    for p in PARMS:
        m[PARMS[p][3]] = PARMS[p][4]

    context['labels'] = [p['label'] for p in FIELDS[displayFields]]
    context['facets'] = [[m[f], facets[f]] for f in facetfields]
    context['fields'] = getfields('FacetLabels')
    context['range'] = range(len(facetfields))
    context['pixonly'] = pixonly
    context['locsonly'] = locsonly
    try:
        context['pane'] = requestObject['pane']
    except:
        context['pane'] = '0'
    try:
        context['resultsOnly'] = requestObject['resultsOnly']
    except:
        pass

    context['imagecount'] = imageCount
    context['url'] = url
    context['querystring'] = querystring
    context['core'] = solr_core
    context['time'] = '%8.3f' % (time.time() - elapsedtime)
    return context

# on startup, do a query to get options values for forms...
context = {'displayType': 'list', 'maxresults': 0,
           'searchValues': {'csv': 'true', 'querystring': '*:*', 'url': '', 'maxfacets': 1000}}
context = doSearch(SOLRSERVER, SOLRCORE, context)

if 'errormsg' in context:
    solrIsUp = False
    print 'Initial solr search failed. Concluding that Solr is down or unreachable... Will not be trying again! Please fix and restart!'
else:
    for facet in context['facets']:
        print 'facet',facet[0],len(facet[1])
        FACETS[facet[0]] = sorted(facet[1])
        #if facet[0] in DROPDOWNS:
        #    FACETS[facet[0]] = sorted(facet[1])
        # if the facet is not in a dropdown, save the memory for something better
        #else:
        #    FACETS[facet[0]] = []
        # build dropdowns for searching
        for f in FIELDS['Search']:
            if f['name'] == facet[0] and f['fieldtype'] == 'dropdown':
                f['dropdowns'] = facet[1]
