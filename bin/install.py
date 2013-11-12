#!/usr/bin/env python

"""
Utility for facilitate dependencies installation
"""

__author__ = 'pruno'

import optparse
import urllib2
import imp
import os
import shutil
import zipfile
import tarfile

os.chdir(os.path.dirname(os.path.realpath(__file__)))

feedparser = imp.load_source('feedparser', './vendor/feedparser.py')

filetypes = [
    'tar.gz',
    'zip',
    'jar'
]


def log(msg):
    print ' > ' + msg


def download(url, path):
    response = urllib2.urlopen(url)
    handle = open(path, 'w')
    handle.write(response.read())
    handle.close()


def get_latest_version_url(package_name):
    global filetypes
    data = feedparser.parse('https://code.google.com/feeds/p/' + package_name + '/downloads/basic')
    for ext in filetypes:
        for entry in data.entries:
            for link in entry.links:
                if link.rel == 'direct':
                    if link.href.endswith(ext):
                        return link.href

    return None


def get_vendor_path():
    return os.path.realpath(__file__ + '/../../../vendor')


def unzip_file(filepath, destination_dir):
    with zipfile.ZipFile(filepath) as zf:
        for member in zf.infolist():
            words = member.filename.split('/')
            path = destination_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zf.extract(member, path)


def untar_file(filepath, destination_dir):
    tar = tarfile.open(filepath)
    tar.extractall(destination_dir)
    tar.close()


def install_package(package_name, use_url=None):
    global filetypes

    log('Installing package ' + package_name)

    if not use_url:
        use_url = get_latest_version_url(package_name)
        if not use_url:
            log('WARN: could not find a valid url for package ' + package_name)
            return

    log('Downloading package from url ' + use_url)

    ext = None
    for i in filetypes:
        if use_url.endswith(i):
            ext = i
            break

    if not ext:
        log('could not understand filetype for ' + use_url)
        return

    filepath = '/tmp/__closure_skeleton_application_' + package_name + '.' + ext
    download(use_url, filepath)
    package_dir = '%s/%s' % (get_vendor_path(), package_name)

    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    os.mkdir(package_dir)
    log('Installing under ' + package_dir)

    if ext == 'jar':
        shutil.move(filepath, '%s/%s.%s' % (package_dir, package_name, ext))

    elif ext == 'tar.gz':
        untar_file(filepath, package_dir)
        os.remove(filepath)

    elif ext == 'zip':
        unzip_file(filepath, package_dir)
        os.remove(filepath)


def install(options):
    if not options.skip_compiler:
        install_package('closure-compiler')

    if not options.skip_templates:
        install_package('closure-templates')

    if not options.skip_stylesheets:
        install_package('closure-stylesheets')

    if not options.skip_linter:
        install_package('closure-linter')


def main():
    usage = 'usage: %prog [options] arg'
    parser = optparse.OptionParser(usage)

    parser.add_option('--skip-compiler',
                      action='store_true',
                      dest='skip_compiler',
                      default=False,
                      help='Do not install closure-compiler')

    parser.add_option('--skip-templates',
                      action='store_true',
                      dest='skip_templates',
                      default=False,
                      help='Do not install closure-templates')

    parser.add_option('--skip-stylesheets',
                      action='store_true',
                      dest='skip_stylesheets',
                      default=False,
                      help='Do not install closure-stylesheets')

    parser.add_option('--skip-linter',
                      action='store_true',
                      dest='skip_linter',
                      default=False,
                      help='Do not install closure-linter')

    (options, args) = parser.parse_args()

    install(options)


main()