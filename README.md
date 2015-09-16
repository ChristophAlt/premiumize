# premiumize
Python API for Premiumize.me Torrent Cloud

## Usage

```python

from premiumize import Premiumize

# create a Premiumize object with default domain
p = Premiumize()

# set the credentials for API access
p.set_account('customerId', 'pin')

# add torrent (link or magnet link) to Torrent Cloud
p.add_torrent(magnet:?xt=urn:btih:4391fb534df44c2823377b34faa7e1fea9decf7c&dn=Schubert+Piano+Sheet+Music+-+Public+Domain&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969)

# list the torrents currently in your Torrent Cloud
# if torrent.status is 'finished' the content can be viewed and downloaded via http
for torrent in p.torrents():
  torrent.print_torrent()
  
# list the files contained in the torrent and corresponding dowload links
for torrent in p.torrents():
  for item in torrent.items():
    '{0}: {1}'.format(item.name, item.link)

# remove torrents from Torrent Cloud
for torrent in p.torrents():
  p.remove_torrent(torrent.hash)
  
```
