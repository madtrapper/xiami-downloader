#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import getopt
import sys
import urllib
from urllib2 import build_opener
import urllib2
import xml.etree.ElementTree as ET

URL_PATTERN_ID = 'http://www.xiami.com/song/playlist/id/%d'
URL_PATTERN_SONG = '%s/object_name/default/object_id/0' % URL_PATTERN_ID
URL_PATTERN_ALBUM = '%s/type/1' % URL_PATTERN_ID


def get_playlist_from_url(url):
    print url
    opener = build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(url)
    response_text = response.read()
    print response_text
    #return parse_playlist(urllib.urlopen(url).read())
    return parse_playlist(response_text)

def parse_playlist(playlist):
    xml = ET.fromstring(playlist)
    return [
        {
            'title': track.find('{http://xspf.org/ns/0/}title').text,
            'location': track.find('{http://xspf.org/ns/0/}location').text
        }
        for track in xml.iter('{http://xspf.org/ns/0/}track')
    ]



def decode_location(location):
    url = location[1:]
    urllen = len(url)
    rows = int(location[0:1])

    cols_base = urllen / rows  # basic column count
    rows_ex = urllen % rows    # count of rows that have 1 more column

    matrix = []
    for r in xrange(rows):
        length = cols_base + 1 if r < rows_ex else cols_base
        matrix.append(url[:length])
        url = url[length:]

    url = ''
    for i in xrange(urllen):
        url += matrix[i % rows][i / rows]

    return urllib.unquote(url).replace('^', '0')

class MyOpener(urllib.FancyURLopener):
     version = 'QuickTime/7.6.2 (verqt=7.6.2;cpu=IA32;so=Mac 10.5.8)'

def download(url, dest):
    #urllib._urlopener = MyOpener()
    #urllib.urlretrieve(url, dest)
    opener = build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    opener.urlretrieve(url, dest)

def dlfile(url, dest):
    # Open the url
    #f = urlopen(url)
    print "downloading : " + url
    opener = build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    checkin_headers = {'Referer':'http://www.xiami.com/web', 'User-Agent':'Opera/9.60',}
    checkin_request = urllib2.Request(url, None, checkin_headers)
    response = opener.open(checkin_request)
    print "downloading2 : " + url

    # Open our local file for writing
    with open(dest, "wb") as local_file:
        local_file.write(response.read())




def usage():
    message = [
        'Usage: %s [options]' % (sys.argv[0]),
        '    -a <album id>: Adds all songs in an album to download list.',
        '    -s <song id>: Adds a song to download list.',
        '    -h : Shows usage.'
    ]
    print '\n'.join(message)


if __name__ == '__main__':
    print 'Xiami Music Preview Downloader'

    playlists = []

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'ha:s:')
    except getopt.GetoptError as e:
        print e
        usage()
        sys.exit(1)

    for key, value in optlist:
        if key == '-a':
            playlists.append(URL_PATTERN_ALBUM % int(value))
            print playlists
        elif key == '-s':
            playlists.append(URL_PATTERN_SONG % int(value))

    if ('-h' in optlist) or (not playlists):
        usage()
        sys.exit(1)

    tracks = []

    for playlist_url in playlists:
        for url in get_playlist_from_url(playlist_url):
            tracks.append(url)

    print '%d file(s) to download' % len(tracks)
    for i in xrange(len(tracks)):
        track = tracks[i]
        filename = '%s.mp3' % track['title']
        print unicode(filename).encode(sys.stdout.encoding, 'replace')
        url = decode_location(track['location'])
        print unicode('[%02d/%02d] Downloading %s...' % (i, len(tracks), filename)).encode(sys.stdout.encoding, 'replace')
        #download(url, filename)
        dlfile(url, filename)
