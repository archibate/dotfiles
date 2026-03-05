#!/usr/bin/python

import subprocess
import os
import glob

names = glob.glob('*.poweramp-backup') + glob.glob('*.flac') + glob.glob('*.mp3')

subprocess.check_call(['adb', 'shell', 'mkdir', '-p', 'storage/emulated/0/song'])

existing_paths = subprocess.check_output(['adb', 'shell', 'ls', 'storage/emulated/0/song/*.{flac,mp3}']).decode().split('\n')
existing_names = []
for path in existing_paths:
    name = os.path.basename(path)
    existing_names.append(name)

for name in names:
    if name not in existing_names:
        print('Pushing', name)
        subprocess.check_call(['adb', 'push', name, 'storage/emulated/0/song/' + name])
    else:
        print('Skipping', name)
