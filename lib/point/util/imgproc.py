from point.util.queue import Queue
#from geweb import log

import settings

# utilities

def make_avatar(path, filename, remove=True, old=None):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'avatar',
        'path': path, 'filename': filename, 'remove': remove, 'old': old})

def move_avatar(old, new):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'move_avatar', 'old': old, 'new': new})

def remove_avatar(filename):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'remove_avatar', 'filename': filename})

def make_attach(path, dest, filename, remove=True):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'attach',
                 'path': path, 'dest': dest, 'filename': filename,
                'remove': remove})

def remove_attach(filename):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'remove_attach', 'filename': filename})

def make_thumbnail(url):
    queue = Queue('imgq', settings.imgproc_socket)
    queue.push({'fn': 'thumbnail', 'url': url})

