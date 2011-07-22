# Copyright (C) 2011, CloudCaptive
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
Created on Jan 21, 2011

@author: shan
'''

import urllib
import string
import logging
from serverside.dao import passphrase_dao

NO_ENCRYPT = True # For Mac OSX pycrypto issues
try:
  from Crypto.Cipher import DES
  NO_ENCRYPT = False
except:
  pass

def aes_encrypt_str(s):
  """ AES encryption using the pycrpyto lib """
  from Crypto.Cipher import AES
  
  for i in range(16-(len(s) % 16)):
    s += " "
  
  enc_obj = AES.new(passphrase_dao.get_aes_encrypt_secret(), AES.MODE_ECB)
  return enc_obj.encrypt(s)

def aes_decrypt_str(s):
  """ AES encryption using the pycrpyto lib """
  from Crypto.Cipher import AES
  enc_obj = AES.new(passphrase_dao.get_aes_encrypt_secret(), AES.MODE_ECB)
  return string.rstrip(enc_obj.decrypt(s))

def des_encrypt_str(str_to_encrypt):
  """DES encryption of string using PyCrypto lib"""
  if NO_ENCRYPT:
    return str_to_encrypt
  enc_obj = DES.new(passphrase_dao.get_encrypt_secret(), DES.MODE_ECB)
  
  logging.info("Input string, about to pad: " + str_to_encrypt + ". Str len: " + str(len(str_to_encrypt)))
  
  """ Convert to UTF-8 encoding """
  str_to_encrypt.encode("utf-8")
  logging.info("THE UTF-8 String: " + str_to_encrypt)
  
  for i in range(8-(len(str_to_encrypt) % 8)):
    str_to_encrypt += " "
  
  logging.info("Input string, padded: " + str_to_encrypt)
  
  return enc_obj.encrypt(str_to_encrypt)
  
  
def des_decrypt_str(str_to_decrypt):
  """DES decryption of string using PyCrypto lib"""
  if NO_ENCRYPT:
    return str_to_decrypt
  enc_obj = DES.new(passphrase_dao.get_encrypt_secret(), DES.MODE_ECB)
  dec_str = enc_obj.decrypt(str_to_decrypt)

  # ISSUE: This throws an unable to encode ascii codec exception
  try:
    dec_str.encode("ascii")
  except:
    logging.error("Unable to encode/decode ascii codec")
    return "" 

  return string.rstrip(dec_str)
  

def simple_encrypt_encode(s):
  """Very simple XOR encryption and url escaping"""
  
  s_xor = xor_str(s)
  return urllib.quote(s_xor, safe="")


def simple_decrpyt_decode(s):
  """Very simple XOR decryption and url unquoting"""
  
  s_unquoted = urllib.unquote(s)
  return xor_str(s_unquoted)

  
def xor_str(s, operand = 1):
  """XOR each element in the string with operand. Returns string"""
  
  b_array = bytearray(s)
  retval = ""
  for b in b_array:
    b = b ^ 1
    retval += str(chr(b))
  return retval
