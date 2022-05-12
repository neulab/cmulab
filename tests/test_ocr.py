#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests

server_url = "http://localhost:8088"
with open(sys.argv[1],'rb') as image_file:
    files = {'file': image_file}
    url = server_url + "/annotator/ocr-post-correction/"
    # will let you know how to get the auth token, have another API for that
    r = requests.post(url, files=files, data={"params": {"threshold": 1}}, headers={"Authorization": "None"})
    print(r.text)
