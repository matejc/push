import gzip
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
import re


def spec(image):
    destination = tempfile.mkdtemp()

    try:
        extract_image(image, destination)
        manifest = scan_directory(destination)
        convert_to_tgzs(manifest)
    except:
        raise
    else:
        return manifest


def extract_image(path, destination):

    def check(members):
        list_members = []
        for tarinfo in members:
            if tarinfo.name is not '.' and tarinfo.name[0] is not '/':
                list_members += [tarinfo]
        return sorted(list_members, key=lambda x: x.name)

    tar = tarfile.open(path)
    tar.extractall(destination, members=check(tar))
    tar.close()

    chmod(destination)


def chmod(directory):
    os.chmod(directory, 0o700)

    for root, subdirs, files in os.walk(directory):
        for d in subdirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            file = os.path.join(root, f)
            os.chmod(file, 0o700)
            if (f == 'layer.tar'):
                os.utime(
                    file, (1466812800, 1466812800))


def scan_directory(imagedir):

    def create_entry(root, subdirs, files):
        entry = {}
        diff_ids = []

        for f in files:
            if f == 'layer.tar':
                entry['tar'] = os.path.join(root, f)
                entry['tar_digest'] = file_digest(entry['tar'])
                diff_ids += [entry['tar_digest']]
            if f == 'json':
                with open(os.path.join(root, f), 'r') as f:
                    entry['spec'] = json.loads(f.read())

        if entry.get('tar') and entry.get('spec'):

            if not entry['spec'].get('history'):
                entry['spec']['history'] = [{
                    'created': entry['spec']['created']
                }]

            if not entry['spec'].get('rootfs'):
                entry['spec']['rootfs'] = {
                    'type': 'layers',
                    'diff_ids': diff_ids
                }

            entry['json'] = json.dumps(entry['spec'], sort_keys=True).encode('utf8')
            hash = hashlib.sha256(entry['json']).hexdigest()
            entry['json_digest'] = "sha256:{hash}".format(hash=hash)

            return entry
        else:
            return None

    repositories = {}
    with open(os.path.join(imagedir, 'repositories'), 'r') as f:
        repositories = json.loads(f.read())

    layers = []
    for root, subdirs, files in os.walk(imagedir):
        entry = create_entry(root, subdirs, files)
        if entry:
            layers += [entry]
    return {
        'root': imagedir,
        'layers': layers,
        'repositories': repositories
    }


def convert_to_tgzs(manifest):
    for layer in manifest['layers']:
        with open(layer['tar'], 'rb') as f_in:
            layer['tgz'] = '{0}{1}layer.tgz'.format(
                os.path.dirname(layer['tar']), os.sep)
            print('Converting layer.tar to {0} ...'.format(layer['tgz']))
            with gzip.open(layer['tgz'], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        patch_tgz(layer['tgz'])
        layer['tgz_digest'] = file_digest(layer['tgz'])
        os.remove(layer['tar'])
        del layer['tar']


def file_digest(path):
    print('Calculating digest for {0} ...'.format(path))
    hasher = hashlib.sha256()
    BLOCKSIZE = 65536
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return 'sha256:{0}'.format(hasher.hexdigest())


def patch_tgz(path):
    # patch mtime
    with open(path, 'r+b') as f:
        f.seek(4)
        f.write(b'\x00\x00\x00\x00')
