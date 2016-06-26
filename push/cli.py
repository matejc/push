#!/usr/bin/env python3

import argparse
import shutil

from push import image
from push import registry


def main():
    parser = argparse.ArgumentParser(
        description='Push image.tar.gz to registry')
    parser.add_argument('image', help='input image, example: ./image.tar.gz')
    parser.add_argument(
        'registry', help='example: http://registry.example.com:5000')
    parser.add_argument(
        '-u', '--username', help='Registry username')
    parser.add_argument(
        '-p', '--password', help='Registry password')
    parser.add_argument(
        '-k', '--keep', action='store_true', help='Keep extracted image')

    args = parser.parse_args()

    try:
        if (args.username is None) ^ (args.password is None):
            raise Exception('username or password missing')
        image_spec = image.spec(args.image)
        registry.push(image_spec, args.registry, args.username, args.password)
    except:
        raise
    else:
        print('Push successful!')
    finally:
        if image_spec and args.keep:
            print('Keeping image directory: {0}'.format(image_spec['root']))
        elif image_spec and len(image_spec['root']) > 10:
            print('Removing {0} ...'.format(image_spec['root']))
            shutil.rmtree(image_spec['root'])


if __name__ == '__main__':
    main()
