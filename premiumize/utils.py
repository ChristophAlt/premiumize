class URL(object):
    
    def __init__(self, base, path):
        self.base = base.rstrip('/')
        self.path = path
        
    @property
    def add(self):
        return self.base + self.path + '/add'
    
    @property
    def list(self):
        return self.base + self.path + '/list'
    
    @property
    def remove(self):
        return self.base + self.path + '/delete'
    
    @property
    def browse(self):
        return self.base + '/browsetorrent'