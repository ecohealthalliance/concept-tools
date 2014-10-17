#!/usr/bin/env python
"""
Combine data from the

    crosswiki_dictionary
    crosswiki_invdict
    dbpedia_geo
    geoname_links

You'll want to make an index on the geonameid property in the
geoanmes.allCountries collection, e.g.:

db.allCountries.ensureIndex({geonameid: 1})

"""

import sys
import re
import codecs
import argparse
import urllib

from pymongo import MongoClient


class LocationMigrator():

    client = MongoClient('mongodb://localhost:27017/')
    db = client.concepts
    dbpedia_geo_coll = db.dbpedia_geo
    wikidata_geo_coll = db.wikidata_geo
    geoname_links_coll = db.geoname_links
    crosswiki_dictionary = db.crosswiki_dictionary
    forms_coll = db.forms
    concepts_coll = db.concepts
    all_countries_coll = client.geonames.allCountries

    concepts_coll.ensure_index('type')
    dbpedia_geo_coll.ensure_index('geonameid')

    def migrate(self):

        dict_results = self.crosswiki_dictionary.find(timeout=False)

        i = 0

        for dict_result in dict_results:

            location_concepts = []

            for concept in dict_result['concepts']:
                if self.has_geo_info(concept['id']):
                    location_concepts.append(
                        { 'id': concept['id'],
                          'counts': concept['counts'],
                          'prob': concept['prob'] } )

            if len(location_concepts) > 0:
                self.forms_coll.insert(
                    { '_id': dict_result['_id'],
                      'counts': dict_result['counts'],
                      'concepts': location_concepts } )
            i += 1
            if i % 1000 == 0:
                print i
                print 'result:', dict_result
                print "location_concepts", location_concepts
                print


    def has_geo_info(self, concept):
        """Get any geo information we have for a concept title. Geo info could
        be in the geonames db, linked via the geoname_links collection, or it
        could be in the dbpedia_geo collection.

        There are three ways know that a given concept is a location for which
        we have geo information:

        - we've already added it to concepts with type "location"
        - we can link it up via the geoname_links collection
        - we have a DBPedia geo record for it

        This function determines whether we have any geo information for a concept,
        creates the concepts collection record if necessary, and returns a Boolean
        depending on whether or not there is any geo info.
        """

        if self.concepts_coll.find_one({'_id': concept, 'type': 'location'}):
            return True
        else:
            geoname_record = self.get_geoname_record(concept)

            if geoname_record:
                self.concepts_coll.insert(
                    { '_id': concept,
                      'type': 'location',
                      'lat': geoname_record['lattitude'],
                      'lon': geoname_record['longitude'],
                      'geoname_id': long(geoname_record['geonameid']) } )
                return True
            else:
                dbpedia_coords = self.get_dbpedia_coords(concept)
                if dbpedia_coords:
                    self.concepts_coll.insert(
                        { '_id': concept,
                          'type': 'location',
                          'lat': dbpedia_coords[0],
                          'lon': dbpedia_coords[1] } )
                    return True
                else:
                    wikidata_coords = self.get_wikidata_coords(concept)
                    if wikidata_coords:
                        self.concepts_coll.insert(
                            { '_id': concept,
                              'type': 'location',
                              'lat': wikidata_coords[0],
                              'lon': wikidata_coords[1] } )
                        return True

        return False


    def get_dbpedia_coords(self, concept):

        result = self.dbpedia_geo_coll.find_one({'_id': concept})

        if result:
            return (result['lat'], result['lon'])
        else:
            return None

    def get_wikidata_coords(self, concept):

        result = self.wikidata_geo_coll.find_one({'_id': concept})

        if result:
            return (result['lat'], result['lon'])
        else:
            return None

    def get_geoname_record(self, concept):

        geoname_id = self.get_geoname_id(concept)

        if geoname_id:
            result = self.all_countries_coll.find_one({'geonameid': str(geoname_id)})
        else:
            return None

    def get_geoname_id(self, concept):

        result = self.geoname_links_coll.find_one({'_id': concept})
        if result:
            return result['geoname_id']
        else:
            return None


if __name__ == '__main__':
    lm = LocationMigrator()
    lm.migrate()
