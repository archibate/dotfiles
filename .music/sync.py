#!/usr/bin/python

'''
$num($add(10000,$replace($replace(%replaygain_track_gain%,.,),dB,)),8)
'''

import subprocess
import argparse
import shlex
import os

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--create', action='store_true')
ap.add_argument('-R', '--upload-remove', action='store_true')
ap.add_argument('-d', '--download', action='store_true')
ap.add_argument('-u', '--upload', action='store_true')
ap.add_argument('-r', '--remove', action='store_true')
ap.add_argument('-C', '--upload-create', action='store_true')
args = ap.parse_args()

if 1:
    # remote_dir = 'storage/emulated/0/Download/netease/cloudmusic/Music/'
    remote_dir = 'storage/emulated/0/Download/netease/cloudmusic/Dj'
    remote_dirs = [
        'storage/emulated/0/qqmusic/song/*.flac',
        'storage/emulated/0/qqmusic/song/*.mp3',
        'storage/emulated/0/Download/netease/cloudmusic/Music/*.flac',
        'storage/emulated/0/Download/netease/cloudmusic/Music/*.mp3',
        'storage/emulated/0/Download/netease/cloudmusic/Dj/*.flac',
        'storage/emulated/0/Download/netease/cloudmusic/Dj/*.mp3',
        'storage/emulated/0/Music/bilibili/*.flac',
        'storage/emulated/0/Music/bilibili/*.mp3',
    ]
else:
    remote_dir = 'storage/emulated/0/song/'
    remote_dirs = [
        'storage/emulated/0/song/*.{flac,mp3}',
    ]

local_dirs = [
    '*.{flac,mp3}',
]

try:
    paths = subprocess.check_output(['adb', 'shell', 'ls', *remote_dirs]).decode().split('\n')
except UnicodeDecodeError as e:
    code = subprocess.check_output(['adb', 'shell', 'ls', *remote_dirs])
    code = code.decode('utf-8', 'replace')
    i = code.find('\ufffd')
    if i != -1:
        print(i, code[max(0,i-50):i+50])
    raise e

visited = set()
for path in paths:
    if not path:
        continue

    name = os.path.basename(path)
    visited.add(name)

    if not os.path.exists(name):
        print('[+]', name)
        if args.create:
            subprocess.check_call(['adb', 'pull', '-z', 'any', path, name])
        if args.upload_remove:
            # subprocess.check_call(['adb', 'shell', 'mv', shlex.quote(path), shlex.quote(path + '.backup')])
            subprocess.check_call(['adb', 'shell', 'rm', shlex.quote(path)])

    else:
        mtime = float(subprocess.check_output(['adb', 'shell', 'stat', '-c', '%Y', shlex.quote(path)]).strip())

        eps = 5
        dt = mtime - os.stat(name).st_mtime

        if dt > eps:
            print('[v]', name, int(dt))
            if args.download:
                subprocess.check_call(['adb', 'pull', '-z', 'any', path, name])
            continue

        if dt < -eps:
            print('[^]', name, int(dt))
            if args.upload:
                subprocess.check_call(['adb', 'push', '-z', 'any', name, path])
            continue

        print('[ ]', name)

names = subprocess.check_output(['sh', '-c', 'ls ' + ' '.join(local_dirs)]).decode().split('\n')

for name in names:
    if not name:
        continue

    if name not in visited:
        print('[-]', name)
        if args.upload_create:
            path = remote_dir + '/' + name
            subprocess.check_call(['adb', 'push', '-z', 'any', name, path])
        if args.remove:
            os.unlink(name)
