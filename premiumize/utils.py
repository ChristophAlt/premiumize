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