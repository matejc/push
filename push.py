#!/usr/bin/env python3

import requests
import json
import hashlib

url = 'http://localhost:5000'


name = 'my-echo'
tag = 'ovce'


filePath = './d87fff53a60131e2b81299a9b0ff43fef8705bbd568ea5ddbfa44266ab88c58e/layer.tgz'
digest1 = 'sha256:20ceb80c7191c427f3732f8ce58a1186f8a916b70aaa76d296bf55f170e0d3b9' # layer.tar
digest = 'sha256:e1a374f2155b39e0b4712a4c5f9803d17b19a8516468a04b3f674a02b5ef8f2a' # layer.tgz

data = open(filePath, 'rb').read()

headers = {}

r = requests.post('{url}/v2/{name}/blobs/uploads/'.format(url=url, name=name), headers=headers)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)

uploadURL = r.headers['Location']

datalen = len(data)
headers = {'Content-Type': 'application/vnd.docker.image.rootfs.diff.tar.gzip'}
r = requests.put('{uploadURL}&digest={digest}'.format(uploadURL=uploadURL, digest=digest), headers=headers, data=data)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)


headers = {}
r = requests.head('{url}/v2/{name}/blobs/{digest}'.format(url=url, name=name, digest=digest), headers=headers)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)
datalen2 = int(r.headers['Content-Length'])



headers = {}
r = requests.post('{url}/v2/{name}/blobs/uploads/'.format(url=url, name=name), headers=headers)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)

uploadURL = r.headers['Location']

obj = {
 "architecture": "amd64",
 "config": {
  "Cmd": [
   "/nix/store/hbgd7mbpylfz6zxj5bkdyi07yag77b8l-bash-4.3-p42/bin/bash",
   "-c",
   "echo my hello!"
  ]
 },
 "created": "1970-01-01T00:00:01Z",
 "os": "linux",
 "history": [{
    "created": "1970-01-01T00:00:01Z"
  }],
  "rootfs": {
    "type": "layers",
    "diff_ids": [digest1]
  }
}


data = json.dumps(obj).encode('utf8')



configlen = len(data)

hash = hashlib.sha256(data).hexdigest()
configdigest = "sha256:{hash}".format(hash=hash)


headers = {'Content-Type': 'application/vnd.docker.container.image.v1+json'}
r = requests.put('{uploadURL}&digest={digest}'.format(uploadURL=uploadURL, digest=configdigest), headers=headers, data=data)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)


headers = {}
r = requests.head('{url}/v2/{name}/blobs/{digest}'.format(url=url, name=name, digest=configdigest), headers=headers)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)
configlen2 = int(r.headers['Content-Length'])

obj = {
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
   "config": {
      "mediaType": "application/vnd.docker.container.image.v1+json",
      "size": configlen2,
      "digest": configdigest
   },
   "layers": [
      {
         "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
         "size": datalen2,
         "digest": digest
      }
   ]
}

json = json.dumps(obj).encode('utf8')

headers = {'Content-Type': 'application/vnd.docker.distribution.manifest.v2+json'}

r = requests.put('{url}/v2/{name}/manifests/{reference}'.format(url=url, name=name, reference=tag), headers=headers, data=json)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)


r = requests.head('{url}/v2/{name}/manifests/{reference}'.format(url=url, name=name, reference=tag), headers=headers)
print(r.url)
print(r.status_code)
print(r.headers)
print(r.text)

