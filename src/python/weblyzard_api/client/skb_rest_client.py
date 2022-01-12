#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Oct 24, 2016

@author: stefan
'''

from builtins import object
import json
import logging
from typing import List, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


class SKBRESTClient(object):

    VERSION = 1.0
    TRANSLATION_PATH = '{}/skb/translation?'.format(VERSION)
    TITLE_TRANSLATION_PATH = '{}/skb/title_translation?'.format(VERSION)
    ENTITY_PATH = '{}/skb/entity'.format(VERSION)
    ENTITY_BATCH_PATH = '{}/skb/entity_batch'.format(VERSION)
    ENTITY_URI_BATCH_PATH = '{}/skb/entity_uri_batch'.format(VERSION)
    # ENTITY_BY_PROPERTY_PATH = '{}/skb/entity_by_property'.format(VERSION)
    ENTITY_SEARCH_PATH = '{}/skb/entity/search'.format(VERSION)

    def __init__(self, url):
        '''
        :param url: URL of the SKB web service
        '''
        self.url = url

    def translate(self, **kwargs):
        response = requests.get(
            '%s/%s' % (self.url, self.TRANSLATION_PATH), params=kwargs)
        if response.status_code < 400:
            return(response.text, kwargs['target'])
        else:
            return None

    def title_translate(self, **kwargs):
        response = requests.get(
            '%s/%s' % (self.url, self.TITLE_TRANSLATION_PATH), params=kwargs)
        if response.status_code < 400:
            return(response.text, kwargs['target'])
        else:
            return None

    def clean_keyword_data(self, kwargs):
        """
        Prepare the keyword entity for SKB submission.
        :param kwargs
        """
        uri = kwargs['key']

        lang = None
        general_pos = None

        if uri.startswith('wl:'):
            lang, kw = uri.split(':')[1].split('/')
            uri = 'skbkw{}:{}'.format(lang, kw.replace(' ', '_'))
        elif uri.startswith('http://weblyzard.com/skb/keyword/'):
            stripped_uri = uri[len('http://weblyzard.com/skb/keyword/'):]
            uri_elements = stripped_uri.split('/')
            if len(uri_elements) == 3:  # lang, pos, kw
                lang = uri_elements[0]
                general_pos = uri_elements[1]
            elif len(uri_elements) == 2 and len(uri_elements[0]) == 2:  # lang, kw
                lang = uri_elements[0]

        preferredName = kwargs.get(
            'preferred_name', kwargs.get('preferredName', None))
        skb_relevant_data = {'uri': uri,
                             'preferredName': '{}@{}'.format(preferredName, lang) if lang else preferredName,
                             'entityType': kwargs.get('entity_type', kwargs.get('entityType', None)),
                             'provenance': kwargs['provenance']}
        if general_pos:
            skb_relevant_data['lexinfo:partOfSpeech'] = general_pos
        return skb_relevant_data

    def clean_recognize_data(self, kwargs):
        '''
        Helper fn that takes the data generated from recognyze and keeps
        only the properties, preferred Name, entityType, uri and profileName
        as provenance, if set.

        :param kwargs: The keyword data.
        :type kwargs: dict
        :returns: THe cleaned data.
        :rtype: dict
        '''
        skb_relevant_data = kwargs.get('properties', {})
        for key in ('entityType', 'preferredName'):
            if key in kwargs:
                skb_relevant_data[key] = kwargs[key]
        skb_relevant_data['uri'] = kwargs['key']
        if 'profileName' in kwargs:
            skb_relevant_data['provenance'] = kwargs['profileName']
        return skb_relevant_data

    def save_doc_kw_skb(self, kwargs):
        '''
        Saves the data for a keyword to the SKB, cleaning it first
        from document-specific information.

        :param kwargs: The entity data
        :type kwargs: dict
        :returns: The entity's uri.
        :rtype: str or unicode
        '''
        skb_relevant_data = self.clean_keyword_data(kwargs)
        return self.save_entity(entity_dict=skb_relevant_data)

    def save_entity(self, entity_dict:dict, force_update:bool=False,
                    ignore_cache:bool=False) -> Optional[dict]:
        '''
        Save an entity to the SKB, the Entity encoded as `dict`.
        The `entity_dict` must contain a 'uri' and an 'entityType' entry
        and the 'provenance', i.e. an identifier how the entity's information 
        got obtained (e.g. repository, profiles, query/script etc. used).

        If no URI is sent the SKB attempts to compile a weblyzard-namespaced custom
        entity URI from the preferredName or a name rdf predicate (this needs to exist).

        :param entity_dict: the entity as dict
        :param force_update: force a comparison and update on any existing SKB values
        :param ignore_cache: bypass recently requested URI cache
        :returns: json response as dict or None, if an error occurred

        >>> response = skb_client.save_entity({
            "entityType": "OrganizationEntity",
            "provenance": "custom_entity_20210101",
            "rdfs:label": "Hello world!",
            "thumbnail": "https://s0.wp.com/i/blank.jpg",
            "twitter": "@HelloWorld",
        })
        >>> print(response) = {
            "data": {
                    "entityType": "OrganizationEntity",
                    "uri": "http://weblyzard.com/skb/entity/organization/hello_world",
                    "preferredName": "Hello world!"
                    "preferredNameByLang": "Hello world!"
                    "rdfs:label": "Hello world!",
                    "wdt:P18": "https://s0.wp.com/i/blank.jpg",
                    "twitter username": "@HelloWorld",
            },
            "uri": "http://weblyzard.com/skb/entity/organization/hello_world",
            "message": "success",
            "info": "added entity",
            "reason": null,
            "status": 200
        }
        '''
        assert 'entityType' in entity_dict
        assert 'provenance' in entity_dict

        params = {'force_update': force_update,
                  'ignore_cache': ignore_cache}

        response = requests.post(url=f'{self.url}/{self.ENTITY_PATH}',
                                 params=params,
                                 json=entity_dict,
                                 )
        return self.drop_error_responses(response)

    def drop_error_responses(self, response):
        if response.status_code < 400:
            return json.loads(response.text)
        else:
            return None

    def save_entity_uri_batch(self, uri_list:List[str], language:str, force_update:bool=False,
                              ignore_cache:bool=False) -> Optional[dict]:
        '''
        Send a batch of shortened entity URIs to the SKB for storage.
        :param uri_list: list of shorted URIs of one of those forms
                1.'{entity_type abbr}:{repository abbr}:{id}'
                with entity_type abbr: P, G, O, E and short repository: wd, osm, gn
                2. '{entity_type}:{entity uri}
                e.g. 'RocheEntity:http://ontology.roche.com/ROX1305279964642'
        :param language: language filter for preferredName result
        :param force_update: update existing SKB values via Jairo
        :param ignore_cache: bypass recently requested URI cache
        :returns: json response as dict or None, if an error occurred
        '''

        if len(uri_list) < 1:
            return None

        params = {'force_update': force_update,
                  'ignore_cache': ignore_cache,
                  'language': language}

        response = requests.post(url=f'{self.url}/{self.ENTITY_URI_BATCH_PATH}',
                                 params=params,
                                 json=uri_list,
                                 )
        return self.drop_error_responses(response)

    def save_entity_batch(self, entity_list:List[dict], force_update:bool=False,
                          ignore_cache:bool=False) -> Optional[dict]:
        '''
        Save a list of entities to the SKB, the individual entities encoded as 
        `dict`. Each `entity_dict` must contain an 'entityType' and a 
        'provenance' entry, which is an identifier how the entity's information 
        got obtained (e.g. repository, profiles, query/script etc. used).

        If no URI is sent the SKB attempts to compile a weblyzard-namespaced custom
        entity URI from the preferredName or a name rdf predicate (this needs to exist).
        
        :param entity_list: entities as list of dicts
        :param force_update: force a comparison and update on any existing SKB values
        :param ignore_cache: bypass recently requested URI cache
        :returns: json response as dict or None, if an error occurred
        
        
        >>> skb_client.save_entity_batch(entity_list=[
            {'entityType': 'PersonEntity', 'provenance': 'unittest', 
            'rdfs:label': 'PersonTest', 'occupation':'wd:Q82955'},
            {'entityType': 'GeoEntity', 'provenance': 'unittest', 
            'gn:name': 'GeoTest', 'gn:alternateName': 'GeographyEntity', 'gn:countryCode':'AT'},
            {'entityType': 'OrganizationEntity', 'provenance': 'unittest', 
            'gn:name': 'OrgTest', 'rdfs:label': ['OrgTest@en', 'OT@de'], 'wdt:P17':'wd:Q40'},
        ])
        >>> print(response) = {
            'success': {'http://weblyzard.com/skb/entity/person/persontest': 'PersonTest', 
                        'http://weblyzard.com/skb/entity/geo/geotest': 'GeoTest', 
                        'http://weblyzard.com/skb/entity/organization/orgtest': 'OrgTest'}, 
            'error': {}, 
            'summary': {'success': 3, 
                        'loaded': 0, 
                        'added': 3, 
                        'updated': 0, 
                        'error': 0, 
                        'total': 3
                        }
        }
        '''

        if len(entity_list) < 1:
            return None

        for entity_dict in entity_list:
            assert 'entityType' in entity_dict
            assert 'provenance' in entity_dict

        params = {'force_update': force_update,
                  'ignore_cache': ignore_cache}

        response = requests.post(url=f'{self.url}/{self.ENTITY_BATCH_PATH}',
                                 params=params,
                                 json=entity_list,
                                 )
        return self.drop_error_responses(response)

    def get_entity_by_property(self, property_value, property_name=None,
                               entity_type=None):
        '''
        Get an entity by a property's value. I.e. one can search for a twitter username
        and get a list of entities and their properties as result. Optionally, one can filter
        by entity_type and property_name (which then has to have `value`).

        It returns a list of dicts containing the properties of the matching entities or None
        if no entities matched.

        :param property_value: The property's value
        :type property_value: str or unicode
        :param property_name: The property's name. Optional.
        :type property_name: str or unicode
        :param entity_type: The type of entity to accept. Optional.
        :type entity_type: str or unicode
        :returns: The data of the entities matching the filter criteria.
        :rtype: list

        >>> skb_client.get_entity_by_property(property_value="You Don't Say")
        [{u'entityType': u'AgentEntity', u'uri': u'http://weblyzard.com/skb/entity/agent/you_don_t_say', u'last_modified': u'2018-05-17T13:16:24.779019', u'_id': u'agent:you_don_t_say', u'properties': {u'url': u'youdontsayaac.com', u'publisher': u"You Don't Say", u'locale': u'en_US', u'twitter_site': u'@mfm_Kay', u'thumbnail': u'https://s0.wp.com/i/blank.jpg'}, u'preferredName': u"You Don't Say"}]
        '''
        params = {'value': property_value}
        if property_name:
            params['property_name'] = property_name
        if entity_type:
            params['entity_type'] = entity_type
        response = requests.get('{}/{}'.format(self.url,
                                               self.ENTITY_BY_PROPERTY_PATH),
                                params=params,
                                headers={'Content-Type': 'application/json'})
        if response.status_code < 400:
            return json.loads(response.text)
        else:
            return None

    def get_entity(self, uri):
        '''
        Get an entity by its uri.

        It returns a dict containing the properties of the entity or None
        if no entities matched.

        :param uri: The uri of the Entity to get.
        :type uri: str or unicode
        :returns: The Entity's data.
        :rtype: dict

        >>> skb_client.get_entity(uri="http://weblyzard.com/skb/entity/agent/you_don_t_say")
        {u'publisher': u"You Don't Say", u'locale': u'en_US', u'entityType': u'AgentEntity', u'thumbnail': u'https://s0.wp.com/i/blank.jpg', u'url': u'youdontsayaac.com', u'twitter_site': u'@mfm_Kay', u'preferredName': u"You Don't Say"}
        '''
        if 'http://weblyzard.com/skb/entity/' in uri:
            uri = uri.replace('http://weblyzard.com/skb/entity/', '')
            prefix = uri.split('/')[0]
            uri = '{}:{}'.format(prefix, '/'.join(uri.split('/')[1:]))
        params = {'uri': uri}
        response = requests.get('{}/{}'.format(self.url,
                                               self.ENTITY_PATH),
                                params=params,
                                headers={'Content-Type': 'application/json'})
        if response.status_code < 400:
            return json.loads(response.text)
        else:
            return None

    def check_entity_exists_in_skb(self, entity, entity_type):
        '''
        Check if a given entity already exists in the SKB. Supports both
        direct (i.e. URI as key) and `owl:sameAs` lookups.
        :param entity
        :param entity_type
        :returns: bool
        '''
        return self.check_existing_entity_key(entity, entity_type) is not None

    def check_existing_entity_key(self, entity, entity_type):
        '''
        If a given entity already exists in the SKB, as identified directly
        (i. e. by URI) or by `owl:sameAs` lookups, return the identifier of
        the existing equivalent entity
        :param entity
        :param entity_type
        :returns: uri of exisiting equivalent entity or None
        '''
        uri = entity.get('uri', entity.get('key', None))

        same_as = entity.get('owl:sameAs', [])
        if isinstance(same_as, str):
            same_as = [same_as]
        for uri in [uri] + same_as:
            try:
                if uri:
                    exact_match = self.get_entity(uri=uri)
                    if exact_match is not None:
                        return exact_match['uri']
                sameas_match = self.get_entity_by_property(
                    property_value=uri,
                    property_name='owl:sameAs',
                    entity_type=entity_type
                )
                if sameas_match is not None and len(sameas_match):
                    logger.info(
                        u'Identified entity {} through sameAs match.'.format(uri))
                    return sameas_match[0]['uri']
            except Exception as e:
                logger.error('Check if entity exists in SKB failed for %s: %s',
                             uri,
                             e)
        return None


class SKBSentimentDictionary(dict):
    SENTIMENT_PATH = '{}/skb/sentiment_dict'.format(SKBRESTClient.VERSION)

    def __init__(self, url, language, emotion='polarity'):
        self.url = '{}/{}'.format(url,
                                  self.SENTIMENT_PATH)
        res = requests.get(self.url,
                           params={'lang': language,
                                   'emotion': emotion})
        if res.status_code < 400:
            response = json.loads(res.text)
            data = {}
            for document in response:
                data[(document['term'], document['pos'])] = document['value']
            dict.__init__(self, data)
        else:
            dict.__init__(self, {})


class SKBSimpleBaseFormsDictionary(dict):
    BASE_FORMS_PATH = '{}/skb/baseforms'.format(SKBRESTClient.VERSION)

    def __init__(self, url):
        self.url = '{}/{}'.format(url, self.BASE_FORMS_PATH)
        res = res = requests.get(self.url)
        if res.status_code < 400:
            response = json.loads(res.text)
            data = self.reconstruct(response)
            dict.__init__(self, data)

    def reconstruct(self, response):
        return_value = {}
        for k, v in response.items():
            return_value[k] = self.reconstruct(v) if isinstance(v, dict) else (set(v) if isinstance(v, list) else v)
        return return_value


if __name__ == '__main__':
    import time

    client = SKBRESTClient(url='http://localhost:5000')
    # # create new entity
    # response = client.save_entity(entity_dict={'entityType': 'PersonEntity', 'provenance': 'unittest', 'rdfs:label': 'TestPerson', 'uri':'http://my_test'})
    # print(response)
    # # update entity
    # response = client.save_entity(entity_dict={'entityType': 'PersonEntity', 'provenance': 'unittest', 'rdfs:label': 'UpdatedTestPerson', 'uri':'http://my_test'}, force_update=True)
    # print(response)
    # time.sleep(3)  # wait to make sure cache was updated
    # response = client.save_entity(entity_dict={'entityType': 'PersonEntity', 'provenance': 'unittest', 'rdfs:label': 'TestPerson', 'uri':'http://my_test'}, force_update=True)
    # print(response)
    # # explicitly ignore cache to update again
    # response = client.save_entity(entity_dict={'entityType': 'PersonEntity', 'provenance': 'unittest', 'rdfs:label': 'TestPerson', 'uri':'http://my_test'}, force_update=True, ignore_cache=True)
    # print(response)

    # response = client.save_entity_uri_batch(uri_list=['P:wd:Q76'], language='en', force_update=False, ignore_cache=False)
    # print(response)
    # response = client.save_entity_uri_batch(uri_list=['PersonEntity:http://www.wikidata.org/entity/Q23'], language='en', force_update=False, ignore_cache=False)
    # print(response)

    response = client.save_entity_batch(entity_list=[{'entityType': 'PersonEntity', 'provenance': 'unittest', 'rdfs:label': 'PersonTest', 'occupation':'wd:Q82955'},
                                                     {'entityType': 'GeoEntity', 'provenance': 'unittest', 'gn:name': 'GeoTest', 'gn:alternateName': 'GeographyEntity', 'gn:countryCode':'AT'},
                                                     {'entityType': 'OrganizationEntity', 'provenance': 'unittest', 'gn:name': 'OrgTest', 'rdfs:label': ['OrgTest@en', 'OT@de'], 'wdt:P17':'wd:Q40'},
                                                     ])
    print(response)
    {'success': {'http://weblyzard.com/skb/entity/person/persontest': 'PersonTest',
                 'http://weblyzard.com/skb/entity/geo/geotest': 'GeoTest',
                 'http://weblyzard.com/skb/entity/organization/orgtest': 'OrgTest'},
     'error': {},
     'summary': {'success': 3,
                 'loaded': 0,
                 'added': 3,
                 'updated': 0,
                 'error': 0,
                 'total': 3}}

