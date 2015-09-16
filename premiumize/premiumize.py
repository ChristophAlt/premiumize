#!/usr/bin/env python

"""
Unofficial Python API for Premiumize.me Downloader (Torrent Cloud and Filehoster).
Currently supports listing, adding and removing torrents as well as getting links for filehosters.

@author Christoph Alt
@email chrizz.alt@gmail.com
"""

import requests
from functools import partial
from lxml import html
from utils import URL


class Premiumize(object):
    def __init__(self, base_url='https://www.premiumize.me', torrent_path='/torrent', filehost_path='/filehost'):
        """
        Premiumize.me torrent cloud API including adding, removing and listing torrents and the
        corresponding download links to all files of each torrent

        :param base_url: the url Premiumize.me can be reached
        :param path: path to the torrent cloud API
        :returns: Premiumize object to interact with torrent cloud
        """

        self.base_url = base_url
        self.torrent_path = torrent_path
        self.filehost_path = filehost_path

    def set_account(self, customer_id, pin):
        """
        Sets the credentials used to access the API

        :param customerId: the customer id is used as the user name for authentication
        :param pin: the pin is used as a password for authentication
        """

        self.customer_id = customer_id
        self.pin = pin

    def torrent_cloud(self):
        url = URL(self.base_url, self.torrent_path, self.filehost_path)
        return TorrentCloud(url, self.customer_id, self.pin)

    def filehoster(self):
        url = URL(self.base_url, self.torrent_path, self.filehost_path)
        return Filehoster(url, self.customer_id, self.pin)


class TorrentCloud(object):
    def __init__(self, url, customer_id, pin):
        self.url = url
        self.customer_id = customer_id
        self.pin = pin
        self.headers = {'cookie': 'login={0}:{1}'.format(self.customer_id, self.pin)}

    def __iter__(self):
        return self.torrents()

    def torrents(self):
        """
        Lists all torrents currently added to the users account

        :returns: an iterator over all torrents
        """

        request = requests.get(self.url.torrent_list,
                               headers=self.headers)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])
        torrents = [self._build_torrent(torrent) for torrent in
                    request_json['torrents']]
        for torrent in torrents:
            yield torrent

    def add(self, link):
        """
        Adds a torrent to the users account, in case it is already cached, it's immediately available for download

        :param link: a magnet or torrent link
        """

        payload = {'url': link, 'seed': '2or48h'}
        request = requests.post(self.url.torrent_add,
                                headers=self.headers,
                                data=payload)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])

    def remove(self, hash):
        """
        Removes a torrent from the users account

        :param hash: the hash of the torrent to be removed
        """

        payload = {'hash': hash.lower()}
        request = requests.post(self.url.torrent_remove,
                                headers=self.headers,
                                data=payload)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])

    def _build_torrent(self, torrent):
        """
        Creates a torrent object from an API response

        :param torrent: a json object containing information about the torrent
        :returns: a Torrent object
        """

        request = partial(requests.get,
                          self.url.torrent_browse,
                          headers=self.headers)

        eta = leecher = seeder = speed_up = speed_down = percent_done = ratio = 0
        if torrent['eta']: eta = int(torrent['eta'])
        if torrent['leecher']: leecher = int(torrent['leecher'])
        if torrent['percent_done']: percent_done = float(torrent['percent_done'])
        if torrent['ratio']: ratio = float(torrent['ratio'])
        if torrent['seeder']: seeder = int(torrent['seeder'])
        if torrent['speed_down']: speed_down = float(torrent['speed_down'])
        if torrent['speed_up']: speed_up = float(torrent['speed_up'])

        return Torrent(eta,
                       torrent['hash'],
                       leecher,
                       torrent['name'],
                       percent_done,
                       ratio,
                       seeder,
                       torrent['size'],
                       speed_down,
                       speed_up,
                       torrent['status'],
                       request)


class Filehoster(object):
    def __init__(self, url, customer_id, pin):
        self.url = url
        self.customer_id = customer_id
        self.pin = pin
        self.headers = {'cookie': 'login={0}:{1}'.format(self.customer_id, self.pin)}

    def get(self, link):
        """
        Get the download link for a file hosted on one of the supported filehosters

        :param link: a filehoster link
        """

        payload = {'url': link}
        request = requests.post(self.url.filehost_get_link,
                                headers=self.headers,
                                data=payload)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])
        return self._build_hoster_file(request_json)

    def _build_hoster_file(self, file):
        stream_location = ''
        if file['stream_location']:
            stream_location = file['stream_location']
        size = 0
        if file['filesize'] != 'Size not available':
            size = long(file['filesize'])

        return HosterFile(file['filename'],
                          size,
                          file['location'],
                          stream_location)


class Torrent(object):
    """
    The object stores all related information and can be used to retrieve the file list and download links
    of a torrent stored in the torrent cloud
    """

    def __init__(self, eta, hash, leecher, name, percent_done,
                 ratio, seeder, size, speed_down, speed_up, status, request):
        self.seeder = seeder
        self.eta = eta
        self.leecher = leecher
        self.percent_done = percent_done
        self.ratio = ratio
        self.speed_down = speed_down
        self.speed_up = speed_up
        self.hash = hash
        self.name = name
        self.size = size
        self.status = status
        self._request = request

    def __iter__(self):
        return self.items()

    def items(self):
        """
        Lists all items of a torrent

        :returns: an iterator over all items (files) of a torrent and its corresponding dowload link
        """

        params = {'hash': self.hash}
        request = self._request(params=params)
        tree = html.fromstring(request.text)
        links = tree.xpath('//a[@class="btn btn-primary btn-xs"]/@href')
        item_list = []
        for link in links:
            if not link.startswith('/player'):
                item_list.append(link)
        for link in item_list:
            yield Item(link)

    def __repr__(self):
        return self.name

    def print_torrent(self):
        """
        Print torrent details
        """

        print('Name: %s' % self.name)
        print('Status: %s' % self.status)
        print('Seeder: %d' % self.seeder)
        print('Leecher: %d' % self.leecher)
        print('Size: %d' % self.size)
        print('Percent done: %d' % self.percent_done)
        print('Eta: %d' % self.eta)
        print('Hash: %s' % self.hash)
        print('Ratio: %d' % self.ratio)
        print('Speed down: %d' % self.speed_down)
        print('Speed up: %d' % self.speed_up)


class Item(object):
    def __init__(self, link):
        self.name = requests.utils.unquote(link.split('/')[-1])
        self.link = link


class HosterFile(object):
    """
    The object stores all related information about a filehoster file
    """

    def __init__(self, name, size, location, stream_location):
        self.name = name
        self.size = size
        self.location = location
        self.stream_location = stream_location

    def print_file(self):
        """
        Print file details
        """

        print('Name: %s' % self.name)
        print('Size: %d' % self.size)
        print('Location: %s' % self.location)
        print('Stream Location: %s' % self.stream_location)
