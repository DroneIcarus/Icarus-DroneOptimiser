#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Signs a URL using a URL signing secret
    Credits: https://github.com/googlemaps/url-signing/blob/gh-pages/urlsigner.py
"""

import hashlib
import hmac
import base64
from urllib.parse import urlparse


def sign_url(input_url=None, secret=None):
  """ Sign a request URL with a URL signing secret.

      Usage:
      from UrlSigner import sign_url

      signed_url = sign_url(input_url=my_url, secret=SECRET)

      Args:
      input_url - The URL to sign
      secret    - Your URL signing secret

      Returns:
      The signed request URL
  """

  if not input_url and not secret:
    raise Exception("Both input_url and secret are required")

  url = urlparse(input_url)

  # We only need to sign the path+query part of the string
  url_to_sign = (url.path + "?" + url.query).encode("utf-8")

  # Decode the private key into its binary format
  # We need to decode the URL-encoded private key
  decoded_key = base64.urlsafe_b64decode(secret)

  # Create a signature using the private key and the URL-encoded
  # string using HMAC SHA1. This signature will be binary.
  signature = hmac.new(decoded_key, url_to_sign, hashlib.sha1)

  # Encode the binary signature into base64 for use within a URL
  encoded_signature = ( base64.urlsafe_b64encode(signature.digest()) ).decode("utf-8")

  signed_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query + "&signature=" + encoded_signature

  # Return signed URL
  return signed_url

if __name__ == "__main__":
  input_url = input("URL to Sign: ")
  secret = input("URL signing secret: ")
  print("Signed URL: " + sign_url(input_url, secret))
