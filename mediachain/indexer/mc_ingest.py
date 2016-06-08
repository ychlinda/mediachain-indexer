#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = \
"""
Functions for ingestion of media files into Indexer.

Potential sources include:
- Mediachain blockchain.
- Getty dumps.
- Other media sources.

Scraping / downloading functions also contained here.

Later may be extended to insert media that comes from off-chain into the chain.
"""

from mc_generic import setup_main, group, raw_input_enter, pretty_print

import mc_config

import mc_datasets

from time import sleep
import json
import os
from os.path import exists, join
from os import mkdir, listdir, walk, unlink
from Queue import Queue
from threading import current_thread,Thread

import requests
from random import shuffle
from shutil import copyfile
import sys
from sys import exit

from datetime import datetime
from dateutil import parser as date_parser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from hashlib import md5

from PIL import Image
from cStringIO import StringIO

import binascii
import base64
import base58

import numpy as np

import imagehash
import itertools

    
data_pat = 'data:image/jpeg;base64,'
data_pat_2 = 'data:image/png;base64,'
    
def shrink_and_encode_image(s, size = (150, 150)):
    """
    Resize image to small size & base64 encode it.
    """
    
    img = Image.open(StringIO(s))
    
    if (img.size[0] > size[0]) or (img.size[1] > size[1]):
        f2 = StringIO()
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(f2, "JPEG")
        f2.seek(0)
        s = f2.read()
    
    return data_pat + base64.urlsafe_b64encode(s)

def decode_image(s):

    if s.startswith(data_pat):
        ss = s[len(data_pat):]
        
    elif s.startswith(data_pat_2):
        ss = s[len(data_pat_2):]
        
    else:
        assert False,('BAD_DATA_URL',s[:15])
        
    return base64.urlsafe_b64decode(ss)


def es_connect():
    print ('CONNECTING...')
    es = Elasticsearch()
    print ('CONNECTED')
    return es

        
def ingest_bulk(iter_json = False,
                thread_count = 1,
                index_name = mc_config.MC_INDEX_NAME,
                doc_type = mc_config.MC_DOC_TYPE,
                search_after = False,
                redo_thumbs = True,
                ignore_thumbs = False,
                delete_current = True,
                ):
    """
    Ingest Getty dumps from JSON files.

    Currently does not attempt to import media to the Mediachain chain.
    
    Args:
        iter_json:      Iterable of media objects, with `img_data` containing the raw-bytes image data.
        thread_count:   Number of parallel threads to use for ES insertion.
        index_name:     ES index name to use.
        doc_type:       ES document type to use.
        search_after:   Manually inspect ingested records after. Probably not needed anymore.
        redo_thumbs:    Whether to recalcuate 'image_thumb' from 'img_data'.
        ignore_thumbs:  Whether to ignore thumbnail generation entirely.
        delete_current: Whether to delete current index, if it exists.

    Returns:
        Number of inserted records.

    Examples:
        See `mc_test.py`
    """

    if not iter_json:
        iter_json = mc_datasets.iter_json_getty(index_name = index_name,
                                                doc_type = doc_type,
                                                )
    
    es = es_connect()
    
    if delete_current and es.indices.exists(index_name):
        print ('DELETE_INDEX...', index_name)
        es.indices.delete(index = index_name)
        print ('DELETED')
            
    print ('CREATE_INDEX...',index_name)
    es.indices.create(index = index_name,
                      body = {'settings': {'number_of_shards': mc_config.MC_NUMBER_OF_SHARDS,
                                           'number_of_replicas': mc_config.MC_NUMBER_OF_REPLICAS,                             
                                           },
                              'mappings': {doc_type: {'properties': {'title':{'type':'string'},
                                                                     'artist':{'type':'string'},
                                                                     'collection_name':{'type':'string'},
                                                                     'caption':{'type':'string'},
                                                                     'editorial_source':{'type':'string'},
                                                                     'keywords':{'type':'string', 'index':'not_analyzed'},
                                                                     'created_date':{'type':'date'},
                                                                     'image_thumb':{'type':'string', 'index':'no'},
                                                                     'dedupe_hsh':{'type':'string', 'index':'not_analyzed'},
                                                                     },
                                                      },
                                           },
                              },
                      #ignore = 400, # ignore already existing index
                      )
    
    print('CREATED',index_name)
    
    print('INSERTING...')

    def iter_wrap():
        # Put in parallel_bulk() format:
        
        for hh in iter_json:
            
            xdoc = {'_op_type': 'index',
                    '_index': index_name,
                    '_type': doc_type,
                    }
            
            hh.update(xdoc)

            if not ignore_thumbs:
                if redo_thumbs:
                    # Check existing thumbs meet size & format requirements:

                    if 'img_data' in hh:
                        hh['image_thumb'] = shrink_and_encode_image(decode_image(hh['img_data']))

                    elif 'image_thumb' in hh:
                        hh['image_thumb'] = shrink_and_encode_image(decode_image(hh['image_thumb']))

                    else:
                        assert False,'CANT_GENERATE_THUMBNAILS'

                elif 'image_thumb' not in hh:
                    # Generate thumbs from raw data:

                    if 'img_data' in hh:
                        hh['image_thumb'] = shrink_and_encode_image(decode_image(hh['img_data']))

                    else:
                        assert False,'CANT_GENERATE_THUMBNAILS'

                if 'img_data' in hh:
                    del hh['img_data']

                yield hh
    
    gen = iter_wrap()

    # TODO: parallel_bulk silently eats exceptions. Here's a quick hack to watch for errors:
        
    first = gen.next()
    
    for is_success,res in parallel_bulk(es,
                                        itertools.chain([first], gen),
                                        thread_count = thread_count,
                                        chunk_size = 500,
                                        max_chunk_bytes = 100 * 1024 * 1024, #100MB
                                        ):
        """
        #FORMAT:
        (True,
            {u'index': {u'_id': u'getty_100113781',
                        u'_index': u'getty_test',
                        u'_shards': {u'failed': 0, u'successful': 1, u'total': 1},
                        u'_type': u'image',
                        u'_version': 1,
                        u'status': 201}})
        """
        pass
        
    print ('REFRESHING', index_name)
    es.indices.refresh(index = index_name)
    print ('REFRESHED')
    
    if search_after:
        
        print ('SEARCH...')
        
        q_body = {"query": {'match_all': {}}}
        
        #q_body = {"query" : {"constant_score":{"filter":{"term":
        #                        { "dedupe_hsh" : '87abc00064dc7e780e0683110488a620e9503ceb9bfccd8632d39823fffcffff'}}}}}

        q_body['from'] = 0
        q_body['size'] = 1

        print ('CLUSTER_STATE:')
        print pretty_print(es.cluster.state())

        print ('QUERY:',repr(q_body))

        res = es.search(index = index_name,
                        body = q_body,
                        )

        print ('RESULTS:', res['hits']['total'])

        #print (res['hits']['hits'])

        for hit in res['hits']['hits']:

            doc = hit['_source']#['doc']

            if 'image_thumb' in doc:
                doc['image_thumb'] = '<removed>'

            print 'HIT:'
            print pretty_print(doc)

            raw_input_enter()


    return es.count(index_name)['count']


"""
EXPECTED ARTEFACT FORMAT:
----

{ 'entity': { u'meta': { u'data': { u'name': u'Randy Brooke'},
                         u'rawRef': { u'@link': '\x12 u\xbb\xdaP\xf6\x1d\x1d\xf4\xff\xcbFD\xac\xe9\x92\xb3,\xf1\x9a;\x08J\r\xd2L\x97\xd0\x8cKY\xd5\x1a'},
                         u'translatedAt': u'2016-06-08T15:25:50.254139',
                         u'translator': u'GettyTranslator/0.1'},
              u'type': u'entity'},
  u'meta': { u'data': { u'_id': u'getty_521396048',
                        u'artist': u'Randy Brooke',
                        u'caption': u'NEW YORK, NY - APRIL 15:  A model walks the runway wearing the Ines Di Santo Bridal Collection Spring 2017 on April 15, 2016 in New York City.  (Photo by Randy Brooke/Getty Images for Ines Di Santo)',
                        u'collection_name': u'Getty Images Entertainment',
                        u'date_created': u'2016-04-15T00:00:00-07:00',
                        u'editorial_source': u'Getty Images North America',
                        u'keywords': [ u'Vertical',
                                       u'Walking',
                                       u'USA',
                                       u'New York City',
                                       u'Catwalk - Stage',
                                       u'Fashion Model',
                                       u'Photography',
                                       u'Arts Culture and Entertainment',
                                       u'Bridal Show'],
                        u'title': u'Ines Di Santo Bridal Collection Spring 2017 - Runway'},
             u'rawRef': { u'@link': "\x12 r\x1a\xed'#\xc8\xbe\xb1'Qu\xadePG\x01@\x19\x88N\x17\xa9\x01a\x1e\xa9v\xc9L\x00\xe6c"},
             u'translatedAt': u'2016-06-08T15:26:12.622240',
             u'translator': u'GettyTranslator/0.1'},
  u'type': u'artefact'}
"""

def ingest_bulk_blockchain(last_block_ref = None,
                           delete_current = True,
                           index_name = mc_config.MC_INDEX_NAME,
                           doc_type = mc_config.MC_DOC_TYPE,
                           ):
    """
    Ingest media from Mediachain blockchain.
    
    Args:
        last_block_ref:  (Optional) Last block ref to start from.
        index_name:      Name of Indexer index to populate.
        doc_type:        Name of Indexer doc type.
    
    """
    
    import mediachain.transactor.client
    from grpc.framework.interfaces.face.face import ExpirationError

    from mediachain.datastore.dynamo import set_aws_config
    
    set_aws_config({'endpoint_url': 'http://localhost:8000',
                    'mediachain_table_name': 'Mediachain',
                    'aws_access_key_id': '',
                    'aws_secret_access_key': '',
                    'region_name':'',
                    })
    
    def the_gen():
        
        while True:
            print 'STREAMING FROM TRANSACTORCLIENT...',(mc_config.MC_TRANSACTOR_HOST,mc_config.MC_TRANSACTOR_PORT)
            
            try:
                
                tc = mediachain.transactor.client.TransactorClient(mc_config.MC_TRANSACTOR_HOST,
                                                                   mc_config.MC_TRANSACTOR_PORT,
                                                                   )
                
                for art in tc.canonical_stream():
                    
                    print 'GOT',art.get('type')
                    
                    if art['type'] != u'artefact':
                        continue
                    
                    meta = art['meta']['data']

                    rh = {}

                    ## Copy these keys in from meta. Use tuples to rename keys. Keys can be repeated:

                    for kk in [u'caption', u'date_created', u'title', u'artist',
                               u'keywords', u'collection_name', u'editorial_source',
                               '_id',
                               ('_id','getty_id'),
                               ]:

                        if type(kk) == tuple:
                            rh[kk[1]] = meta[kk[0]]
                        else:
                            rh[kk] = meta[kk]

                    print art.keys()
                            
                    rh['latest_ref'] = base58.b58encode(art['meta']['rawRef'][u'@link'])

                    #TODO - different created date?:
                    rh['date_created'] = date_parser.parse(art['meta']['translatedAt']) 

                    #TODO: Using this placeholder until we get image data from canonical_stream:
                    rh['img_data'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

                    yield rh
            
                print 'END ITER'
            
            except ExpirationError as e:
                print 'CAUGHT ExpirationError',e
                sleep(1)
                continue
            except:
                #TODO... maybe not nice:
                
                print '!!!FORCE_EXIT'
                
                import traceback, sys, os
                
                for line in traceback.format_exception(*sys.exc_info()):
                    print line,
                
                os._exit(-1)
                
            
            print 'REPEATING...'
            sleep(1)
            
    nn = ingest_bulk(iter_json = the_gen(),
                     index_name = index_name,
                     doc_type = doc_type,
                     delete_current = delete_current,
                     )
    
    print 'DONE_INGEST',nn

    
def ingest_bulk_gettydump(getty_path = 'getty_small/json/images/',
                          index_name = mc_config.MC_INDEX_NAME,
                          doc_type = mc_config.MC_DOC_TYPE,
                          *args,
                          **kw):
    """
    Ingest media from Getty data dumps into Indexer.
    
    Args:
        getty_path: Path to getty image JSON.
        index_name: Name of Indexer index to populate.
        doc_type:   Name of Indexer doc type.
    """
    
    iter_json = mc_datasets.iter_json_getty(getty_path = getty_path,
                                            index_name = index_name,
                                            doc_type = doc_type,
                                            *args,
                                            **kw)

    ingest_bulk(iter_json = iter_json)
    

    
    
def config():
    """
    Print current environment variables.
    """    
    for x in dir(mc_config):
        if x.startswith('MC_'):
            print x + '="%s"' % str(getattr(mc_config, x))


functions=['ingest_bulk_blockchain',
           'ingest_bulk_gettydump',
           'config',
           ]

def main():
    setup_main(functions,
               globals(),
                'mediachain-indexer-ingest',
               )

if __name__ == '__main__':
    main()

