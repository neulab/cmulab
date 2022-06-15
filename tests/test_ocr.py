#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
from pathlib import Path

auth_token = (Path.home() / '.cmulab_elan').read_text().split()[-1]
server_url = "http://localhost:8088"
with open(sys.argv[1],'rb') as image_file1, open(sys.argv[2],'rb') as image_file2:
    files = [('file', image_file1), ('file', image_file2)]
    url = server_url + "/annotator/ocr-post-correction/"
    # will let you know how to get the auth token, have another API for that
    r = requests.post(url, files=files, data={"params": json.dumps({"threshold": 1, "debug": True})}, headers={"Authorization": auth_token})
    print(r.text)
