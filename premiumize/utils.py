import threading
import time


class URL(object):
    
    def __init__(self, base, torrent_path, filehost_path):
        self.base = base.rstrip('/')
        self.torrent_path = torrent_path
        self.filehost_path = filehost_path
        
    @property
    def torrent_add(self):
        return self.base + self.torrent_path + '/add'
    
    @property
    def torrent_list(self):
        return self.base + self.torrent_path + '/list'
    
    @property
    def torrent_remove(self):
        return self.base + self.torrent_path + '/delete'
    
    @property
    def torrent_browse(self):
        return self.base + '/browsetorrent'

    @property
    def filehost_get_link(self):
        return self.base + self.filehost_path + '/getlink'


class TorrentCloudPollingThread(threading.Thread):

    def __init__(self, list_torrents, polling_interval=2):
        super(TorrentCloudPollingThread, self).__init__()
        self.stop = threading.Event()
        self.callbacks = []
        self.polling_interval = polling_interval
        self.list_torrents = list_torrents
        self.running_torrents = []

    def stop(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def add_callback(self, callback):
        if not callback in self.callbacks:
            self.callbacks.append(callback)

    def remove_callback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def run(self):
        while not self.stopped():
            torrents = self.list_torrents()
            for torrent in torrents:
                if torrent.status != 'finished' and torrent.hash not in self.running_torrents:
                    self.running_torrents.append(torrent.hash)
                elif torrent.status == 'finished' and torrent.hash in self.running_torrents:
                    for callback in self.callbacks:
                        callback(torrent)
                    self.running_torrents.remove(torrent.hash)
            time.sleep(self.polling_interval)

