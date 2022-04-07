#!/usr/bin/env python3
# coding:utf-8
# Copyright (C) 2022 All rights reserved.
# FILENAME:  codecs/msgpack.py
# VERSION: 	 0.1.1
# CREATED: 	 2022-04-07 2:08
# AUTHOR: 	 Sitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Standard Packages ###
from typing import Any
### Third-Party Packages ###
from msgpack import dumps, loads
### Local Modules ##
from fastapi_cachette.codecs import Codec

class MsgpackCodec(Codec):

  def dumps(self, obj: Any) -> bytes:
    return dumps(obj)

  def loads(self, data: bytes) -> Any:
    return loads(data)
  