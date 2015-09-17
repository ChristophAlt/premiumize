# premiumize
Python API for Premiumize.me Torrent Cloud

## Usage

```python

from premiumize import Premiumize

# create a Premiumize object with default domain
p = Premiumize()

# set the credentials for API access
p.set_account('customerId', 'pin')

# get torrent cloud handler
torrent_cloud = p.torrent_cloud()

# add torrent (link or magnet link) to Torrent Cloud
torrent_cloud.add('a magnet or torrent link')

# list the torrents currently in your Torrent Cloud
# if torrent.status is 'finished' the content can be viewed and downloaded via http
for torrent in torrent_cloud.torrents():
  torrent.print_torrent()
  
# list the files contained in the torrent and corresponding dowload links
for torrent in torrent_cloud.torrents():
  for item in torrent.items():
    '{0}: {1}'.format(item.name, item.link)

# remove torrents from Torrent Cloud
for torrent in torrent_cloud.torrents():
  torrent_cloud.remove(torrent.hash)
  
# get filehoster handler
filehoster = p.filehoster()

# get link to filehoster file
file = filehoster.get('link to a file hosted on a supported filehoster')
# print information about the file (name, size, location)
file.print_file()
```
