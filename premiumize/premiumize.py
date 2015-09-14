#!/usr/bin/env python

"""
Unofficial Python API for Premiumize.me Torrent Cloud.
Currently supports listing, adding and removing torrents.

@author Christoph Alt
@email chrizz.alt@gmail.com
"""

import requests
from functools import partial
from lxml import html
from utils import URL


class Premiumize(object):
    
    def __init__(self, base_url='https://www.premiumize.me', path='/torrent'):
        """
        Premiumize.me torrent cloud API including adding, removing and listing torrents and the
        corresponding download links to all files of each torrent

        :param base_url: the url Premiumize.me can be reached
        :param path: path to the torrent cloud API
        :returns: Premiumize object to interact with torrent cloud
        """

        self.url = URL(base_url, path)
    
    def set_account(self, customerId, pin):
        """
        Sets the credentials used to access the API

        :param customerId: the customer id is used as the user name for authentication
        :param pin: the pin is used as a password for authentication
        """

        self.customerId = customerId
        self.pin = pin
        self.headers = {'cookie': 'login={0}:{1}'.format(self.customerId, self.pin)}
        
    def __iter__(self):
        return self.torrents()
        
    def torrents(self):
        """
        Lists all torrents currently added to the users account

        :returns: an iterator over all torrents
        """

        request = requests.get(self.url.list,
                               headers=self.headers)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])
        torrents = [self._build_torrent(torrent) for torrent in
                 request_json['torrents']]
        for torrent in torrents:
            yield torrent
            
    def add_torrent(self, link):
        """
        Adds a torrent to the users account, in case it is already cached, it's immediately available for download

        :param link: a magnet or torrent link
        """

        payload = {'url': link, 'seed': '2or48h'}
        request = requests.post(self.url.add,
                                headers=self.headers,
                                data=payload)
        request_json = request.json()
        if request_json['status'] == 'error':
            raise Exception(request_json['message'])
    
    def remove_torrent(self, hash):
        """
        Removes a torrent from the users account

        :param hash: the hash of the torrent to be removed
        """

        payload = {'hash' : hash.lower()}
        request = requests.post(self.url.remove,
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
                          self.url.browse,
                          headers=self.headers)
        
        return Torrent(torrent['eta'],
                      torrent['hash'],
                      torrent['leecher'],
                      torrent['name'],
                      torrent['percent_done'],
                      torrent['ratio'],
                      torrent['seeder'],
                      torrent['size'],
                      torrent['speed_down'],
                      torrent['speed_up'],
                      torrent['status'],
                      request)
        

class Torrent(object):
    """
    The object stores all related information and can be used to retrieve the file list and download links
    of a torrent stored in the torrent cloud
    """
    
    def __init__(self, eta, hash, leecher, name, percent_done,
                 ratio, seeder, size, speed_down, speed_up, status, request):
        self.seeder = 0 if None else seeder
        self.eta = 0 if None else eta
        self.leecher = 0 if None else leecher
        self.percent_done = 0 if None else percent_done
        self.ratio = 0 if None else ratio
        self.speed_down = 0 if None else speed_down
        self.speed_up = 0 if None else speed_up
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