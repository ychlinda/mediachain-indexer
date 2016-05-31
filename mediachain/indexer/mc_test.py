#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = \
"""
Testing.
"""

import datetime
import requests

from mc_generic import setup_main, pretty_print

import mc_config
import mc_ingest
import mc_dedupe

from time import sleep

MC_WEB_HOST = 'http://127.0.0.1:23456'
TEST_INDEX_NAME = 'mc_test'
TEST_DOC_TYPE = 'mc_test_image'

def demo_end_to_end(index_name = TEST_INDEX_NAME,
                    doc_type = TEST_DOC_TYPE,
                    ):
    """
    Quick end-to-end demos. WIP while API is being finalized. TODO: full tests.
    
    1. ingest images.
    2. search for images.
    3. find dupes.

    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    es.search(index='mc_test',body = {"query": {'match_all': {}}})
    """
    
    img_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
    
    img_data = mc_ingest.decode_image(img_uri)

    img_id = 'getty_1234'
    
    test_ingest = [{'_op_type': 'index',
                    '_index': index_name,
                    '_type': doc_type,
                    '_id': img_id,
                    'title':'Crowd of people walking',
                    'artist':'test',
                    'collection_name':'test',
                    'caption':'test',
                    'editorial_source':'',
                    'keywords':'test',
                    'date_created':datetime.datetime.now(),
                    'img_data':img_data,
                    }]
    
    num_inserted = mc_ingest.ingest_bulk(test_ingest,
                                         index_name = index_name,
                                         doc_type = doc_type,
                                         )
    
    print ('INSERTED',num_inserted)

    mc_dedupe.dedupe_reindex(index_name = index_name,
                             doc_type = doc_type,
                             )

    print ('SEARCH_BY_TEXT...')
    
    hh = requests.post(MC_WEB_HOST + '/search',
                       headers = {'User-Agent':'MC_TEST 1.0'},
                       verify = False,
                       json = {"q":'crowd',
                               "limit":5,
                               "include_self": True,
                               "index_name":index_name,
                               "doc_type":doc_type,
                               },
                       ).json()
    
    print pretty_print(hh)
    assert hh['results'][0]['_id'] == img_id,hh
    
    print ('SEARCH_BY_CONTENT...')
    
    hh = requests.post(MC_WEB_HOST + '/search',
                       headers = {'User-Agent':'MC_TEST 1.0'},
                       verify = False,
                       json = {"q_id":img_uri,
                               "limit":5,
                               "include_self": True,
                               "index_name":index_name,
                               "doc_type":doc_type,
                               },
                       ).json()
    
    print pretty_print(hh)
    assert hh['results'][0]['_id'] == img_id,hh

    print ('SEARCH_BY_ID...')
    
    hh = requests.post(MC_WEB_HOST + '/search',
                       headers = {'User-Agent':'MC_TEST 1.0'},
                       verify = False,
                       json = {"q_id":img_id,
                               "limit":5,
                               "include_self": True,
                               "index_name":index_name,
                               "doc_type":doc_type,
                               },
                       ).json()
    
    print pretty_print(hh)
    assert hh['results'][0]['_id'] == img_id,hh
    
    print ('DEDUPE_LOOKUP...')
    
    hh = requests.post(MC_WEB_HOST + '/dupe_lookup',
                       headers = {'User-Agent':'MC_TEST 1.0'},
                       verify = False,
                       #json = {"q_media":img_uri, "limit":5},
                       json = {"q_media":img_id,
                               "limit":5,
                               "include_self": True,
                               "index_name":index_name,
                               "doc_type":doc_type,
                               },
                       ).json()
    
    print pretty_print(hh)
    assert hh['results'][0]['_id'] == img_id,hh

    print ('DONE_DEMO')

functions = ['demo_end_to_end',
             ]

def main():
    setup_main(functions,
               globals(),
               )


if __name__ == '__main__':
    main()
