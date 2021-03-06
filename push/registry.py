import requests
import json
import hashlib


def push(spec, registry, username, password):
    auth = None
    if username and password:
        auth = (username, password)
    is_alive(registry, auth)

    for name in spec['repositories']:

        for tag in spec['repositories'][name]:
            sizes = []

            layer = get_layer(spec, spec['repositories'][name][tag])

            upload_layer(registry, name, tag, layer, auth)

            sizes += [layer['tgz_size'], layer['json_size']]

            uploaded_size = 0
            not_uploaded_count = 0
            for size in sizes:
                if size == -1:
                    not_uploaded_count += 1
                else:
                    uploaded_size += int(size)

            if not_uploaded_count == len(sizes):
                print('[{0}:{1}] Nothing new uploaded'.format(name, tag))
            else:
                upload_manifest(
                    registry,
                    name,
                    tag,
                    spec['layers'][0]['json_size'],
                    spec['layers'][0]['json_digest'],
                    spec['layers'],
                    auth
                )
                print('[{0}:{1}] Uploaded {2:.2f} KiB'.format(
                    name, tag, uploaded_size/1024))


def get_layer(spec, layer_id):
    for layer in spec['layers']:
        if layer['spec']['id'] == layer_id:
            return layer


def upload_layer(registry, name, tag, layer, auth):
    tgz_size = upload(
        registry,
        name,
        tag,
        layer['tgz_digest'],
        'application/vnd.docker.image.rootfs.diff.tar.gzip',
        file=layer['tgz'],
        auth=auth
    )
    layer['tgz_size'] = tgz_size

    json_size = upload(
        registry,
        name,
        tag,
        layer['json_digest'],
        'application/vnd.docker.container.image.v1+json',
        data=layer['json'],
        auth=auth
    )
    layer['json_size'] = json_size


def upload_manifest(
    registry, name, tag, json_size, json_digest, layers, auth=None
):
    manifest = {
       "schemaVersion": 2,
       "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
       "config": {
          "mediaType": "application/vnd.docker.container.image.v1+json",
          "size": int(json_size),
          "digest": json_digest
       },
       "layers": [
       ]
    }

    for layer in layers:
        manifest['layers'] += [{
            "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
            "size": int(layer['tgz_size']),
            "digest": layer['tgz_digest']
        }]

    data = json.dumps(manifest, sort_keys=True).encode('utf8')

    headers = {
        'Content-Type': 'application/vnd.docker.distribution.manifest.v2+json'
    }

    r = requests.put('{registry}/v2/{name}/manifests/{reference}'.format(
        registry=registry, name=name, reference=tag
    ), headers=headers, data=data, auth=auth)

    handle_http_error(r)

    r = requests.head('{registry}/v2/{name}/manifests/{reference}'.format(
        registry=registry, name=name, reference=tag
    ), headers=headers, auth=auth)

    handle_http_error(r)


def upload(
    registry, name, tag, digest, content_type, data=None, file=None, auth=None
):
    r = requests.head('{registry}/v2/{name}/blobs/{digest}'.format(
        registry=registry, name=name, digest=digest), auth=auth)

    handle_http_error(r)

    if r.status_code == 200:
        print('[{0}:{1}] Already exists, skipping {2} ...'.format(
            name, tag, digest[7:19]))
        return -1

    r = requests.post('{registry}/v2/{name}/blobs/uploads/'.format(
        registry=registry, name=name), auth=auth)
    handle_http_error(r)
    uploadURL = r.headers['Location']

    if file and not data:
        data = open(file, 'rb')

    headers = {'Content-Type': content_type}

    print('[{0}:{1}] Pushing {2} ...'.format(name, tag, digest[7:19]))
    r = requests.put('{uploadURL}&digest={digest}'.format(
        uploadURL=uploadURL, digest=digest
    ), headers=headers, auth=auth, data=data)

    handle_http_error(r)

    r = requests.head('{registry}/v2/{name}/blobs/{digest}'.format(
        registry=registry, name=name, digest=digest), auth=auth)

    handle_http_error(r)

    if r.status_code == 200:
        print('[{0}:{1}] Pushed {2}'.format(name, tag, digest[7:19]))
        return r.headers['Content-Length']
    else:
        raise Exception('{0}: {1} {2}'.format(
            r.url, r.status_code, r.text))


def handle_http_error(response):
    if response.status_code not in [200, 201, 202, 404]:
        raise Exception('{0}: {1} {2}'.format(
            response.url, response.status_code, response.text))


def is_alive(registry, auth):
    url = '{0}/v2/'.format(registry)
    r = requests.head(url, auth=auth)
    handle_http_error(r)
    print('Registry {0} is OK'.format(url))
