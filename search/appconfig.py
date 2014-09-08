# set global variables

from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings
import csv


def getParms(parmFile, SUGGESTIONS):
    try:
        f = open(parmFile, 'rb')
        csvfile = csv.reader(f, delimiter="\t")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % parmFile
        return message, -1
    except:
        raise

    try:
        rows = []
        for row, values in enumerate(csvfile):
            rows.append(values)

        return parseRows(rows, SUGGESTIONS)

    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % parmFile
        return message, -1
    except:
        raise


def parseRows(rows, SUGGESTIONS):
    PARMS = {}
    HEADER = {}
    labels = {}
    FIELDS = {}
    functions = 'Search,Facet,bMapper,listDisplay,fullDisplay,gridDisplay,inCSV'.split(',')
    for function in functions:
        FIELDS[function] = []

    fieldkeys = 'label fieldtype suggestions solrfield name order'.split(' ')

    for rowid, row in enumerate(rows):
        rowtype = row[0]

        if rowtype == 'header':
            for i, r in enumerate(row):
                HEADER[i] = r
                labels[r] = i

        elif rowtype == 'field':
            needed = [row[labels[i]] for i in 'Label Role Suggestions SolrField Name'.split(' ')]
            if row[labels['Suggestions']] != '':
                #suggestname = '%s.%s' % (row[labels['Suggestions']], row[labels['Name']])
                suggestname = row[labels['Name']]
            else:
                suggestname = row[labels['Name']]
            needed[4] = suggestname
            PARMS[suggestname] = needed
            needed.append(rowid)

            for function in functions:
                if len(row) > labels[function] and row[labels[function]] != '':
                    fieldhash = {}
                    for n, v in enumerate(needed):
                        fieldhash[fieldkeys[n]] = v
                    fieldhash['style'] = 'width:200px' # temporary hack!
                    FIELDS[function].append(fieldhash)

    return FIELDS, PARMS


def loadConfiguration(configFileName):
    config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), configFileName)

    global MAXMARKERS
    global MAXRESULTS
    global MAXLONGRESULTS
    global MAXFACETS
    global EMAILABLEURL
    global IMAGESERVER
    global CSPACESERVER
    global INSTITUTION
    global BMAPPERSERVER
    global BMAPPERDIR
    global BMAPPERCONFIGFILE
    global SOLRSERVER
    global SOLRCORE
    global LOCALDIR
    global SEARCH_QUALIFIERS
    global FIELDDEFINITIONS
    global CSVPREFIX
    global CSVEXTENSION
    global TITLE
    global SUGGESTIONS
    global LAYOUT
    global LOCATION
    global DROPDOWNS
    global FIELDS
    global PARMS

    try:
        MAXMARKERS = int(config.get('search', 'MAXMARKERS'))
        MAXRESULTS = int(config.get('search', 'MAXRESULTS'))
        MAXLONGRESULTS = int(config.get('search', 'MAXLONGRESULTS'))
        MAXFACETS = int(config.get('search', 'MAXFACETS'))
        EMAILABLEURL = config.get('search', 'EMAILABLEURL')
        IMAGESERVER = config.get('search', 'IMAGESERVER')
        CSPACESERVER = config.get('search', 'CSPACESERVER')
        INSTITUTION = config.get('search', 'INSTITUTION')
        BMAPPERSERVER = config.get('search', 'BMAPPERSERVER')
        BMAPPERDIR = config.get('search', 'BMAPPERDIR')
        BMAPPERCONFIGFILE = config.get('search', 'BMAPPERCONFIGFILE')
        SOLRSERVER = config.get('search', 'SOLRSERVER')
        SOLRCORE = config.get('search', 'SOLRCORE')
        LOCALDIR = config.get('search', 'LOCALDIR')
        SEARCH_QUALIFIERS = config.get('search', 'SEARCH_QUALIFIERS').split(',')
        FIELDDEFINITIONS = config.get('search', 'FIELDDEFINITIONS')
        CSVPREFIX = config.get('search', 'CSVPREFIX')
        CSVEXTENSION = config.get('search', 'CSVEXTENSION')
        TITLE = config.get('search', 'TITLE')
        SUGGESTIONS = config.get('search', 'SUGGESTIONS')
        LAYOUT = config.get('search', 'LAYOUT')
    except:
        print 'error in configuration file %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS)
        print 'this webapp will probably not work'

    # get "frontend" configuration from the ... frontend configuaration file FIELDDEFINITIONS

    print 'reading field definitions from %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS)

    FIELDS, PARMS = getParms(path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS), SUGGESTIONS)

    LOCATION = ''

    DROPDOWNS = []
    for p in PARMS:
        if 'dropdown' in PARMS[p][1]:
            DROPDOWNS.append(PARMS[p][4])
        if 'location' in PARMS[p][1]:
            LOCATION = PARMS[p][3]

    if LOCATION == '':
        print "LOCATION not set, please specify a variable as 'location'"


loadConfiguration('search')