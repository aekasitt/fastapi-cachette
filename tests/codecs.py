#!/usr/bin/env python3
# coding:utf-8
# Copyright (C) 2022 All rights reserved.
# FILENAME:  tests/codecs.py
# VERSION: 	 0.1.1
# CREATED: 	 2022-04-06 22:03
# AUTHOR: 	 Sitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
'''
Test Suite containing different Codec implementations on TestClient
'''
### Standard Packages ###
from decimal import Decimal
from typing import Any, List, NoReturn, Tuple
### Third-Party Packages ###
from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse, Response
from fastapi.testclient import TestClient
from pytest import fixture, FixtureRequest, mark
### Local Modules ###
from fastapi_cachette import Cachette

### Fixtures ###

@fixture(scope='module')
def items() -> List[Any]:
  return [
    None,
    123,                   # Integer
    123.45,                # Float
    'A',                   # Charstring
    'Hello, World!',       # String
    '123',                 # Alphanumeric String of an integer
    '123.45',              # Alphanumeric String of a float
    b'A',                  # Charbytes
    b'Hello, World!',      # Bytes
    b'123',                # Alphanumeric Bytes of an integer
    b'123.45',             # Alphanumeric Bytes of a float
    # { 1, 2, 3 },           # Set of numbers
    # { 'a', 'b', 'c' },     # Set of charstrings
    # { b'a', b'b', b'c' },  # Set of charbytes
    [ 1, 2, 3 ],           # List of numbers
    [ 'a', 'b', 'c' ],     # List of charstrings
    [ b'a', b'b', b'c' ],  # List of charbytes
    # Decimal(12345.67890),  # Decimal
  ]

@fixture(scope='module')
def client(items: List[Any], request: FixtureRequest) -> TestClient:
  configs: List[Tuple[str, Any]] = request.param

  app = FastAPI()

  @Cachette.load_config
  def get_cachette_config():
    return configs

  ### Routing ###
  @app.get('/put-items', response_class=PlainTextResponse, status_code=200)
  async def put_items(cachette: Cachette = Depends()):
    '''
    Puts a list of pre-determined items to cache
    '''
    for i, item in enumerate(items): await cachette.put(f'{ i }', item)
    return 'OK'

  @app.get('/fetch-items', response_class=PlainTextResponse, status_code=200)
  async def fetch_items(cachette: Cachette = Depends()):
    '''
    Returns key value
    '''
    ok: bool = True
    for i, item in enumerate(items):
      uncached: Any = await cachette.fetch(f'{ i }')
      # others
      if uncached != item:
        ok = False
        break
    return ('', 'OK')[ok]

  with TestClient(app) as testclient:
    yield testclient

@mark.parametrize('client', [

  ### DynamoDB & Codecs ###
  [('backend', 'dynamodb'), ('codec', 'msgpack'), ('dynamodb_url', 'http://localhost:8000')], \
  [('backend', 'dynamodb'), ('codec', 'pickle'), ('dynamodb_url', 'http://localhost:8000')],  \

  ### InMemory & Codecs ###
  [('backend', 'inmemory'), ('codec', 'msgpack')], \
  [('backend', 'inmemory'), ('codec', 'pickle')],  \

  ### Memcached & Codecs ###
  [('backend', 'memcached'), ('codec', 'msgpack'), ('memcached_host', 'localhost')], \
  [('backend', 'memcached'), ('codec', 'pickle'), ('memcached_host', 'localhost')],  \

  ### MongoDB & Codecs ###
  [
    ('backend', 'mongodb'), ('database_name', 'fastapi-cachette-database'), \
    ('codec', 'msgpack'), ('mongodb_url', 'mongodb://localhost:27017')      \
  ],
  [
    ('backend', 'mongodb'), ('database_name', 'fastapi-cachette-database'), \
    ('codec', 'pickle'), ('mongodb_url', 'mongodb://localhost:27017')       \
  ],

  ### Redis & Codecs ###
  [('backend', 'redis'), ('codec', 'msgpack'), ('redis_url', 'redis://localhost:6379')], \
  [('backend', 'redis'), ('codec', 'pickle'), ('redis_url', 'redis://localhost:6379')]   \
], ids=[
  'dynamodb-msgpack', 'dynamodb-pickle',
  'inmemory-msgpack', 'inmemory-pickle', 
  'memcached-msgpack', 'memcached-pickle', 
  'mongodb-msgpack', 'mongodb-pickle', 
  'redis-msgpack', 'redis-pickle'
], indirect=True)
def test_every_backend_with_every_codec(client) -> NoReturn:
  response: Response = client.get('/put-items')
  assert response.text == 'OK'
  response = client.get('/fetch-items')
  assert response.text == 'OK'
