#!/usr/bin/env python3

import argparse
import re
import shutil

from pprint import pprint
from push import image
from push import registry


def parse(s):
    address, name, tag = re.match('^(.+/)?([^:]+)(:\w+)?$', s).groups()
    host, port = None, None

    if address is not None:
        host, port = re.match('^([^:]+)(:\d+)?/$', address).groups()
    if port is not None:
        port = port[1:]
    if tag is not None:
        tag = tag[1:]

    return {
       'host': host,
       'port': port,
       'name': name,
       'tag': tag
    }


def main():
    parser = argparse.ArgumentParser(
        description='Push image.tar.gz to registry')
    parser.add_argument('image', help='input image, example: ./image.tar.gz')
    parser.add_argument(
        '-t', '--target', help='[REGISTRY_HOST[:REGISTRY_PORT]/]NAME[:TAG]')

    args = parser.parse_args()

    try:
        image_spec = image.spec(
            args.image, parse(args.target) if args.target else None)
        registry.push(image_spec)
    except:
        raise
    else:
        pprint(image_spec)
    finally:
        if len(image_spec['root']) > 10:
            print('Removing {0} ...'.format(image_spec['root']))
            shutil.rmtree(image_spec['root'])


if __name__ == '__main__':
    main()
