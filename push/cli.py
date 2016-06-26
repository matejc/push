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
    parser.add_argument(
        '-z', '--gzip', action='store_true',
        help='''Compress layers with gzip before uploading, it will take less
                time to upload, but hash will be always different because ctime
                in the header of tgz file will always be different, therefore
                it will be pushed to registry every time all over again'''
    )

    args = parser.parse_args()

    try:
        if (args.username is None) ^ (args.password is None):
            raise Exception('username or password missing')
        image_spec = image.spec(args.image, do_not_compress=not args.gzip)
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
