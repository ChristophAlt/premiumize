# premiumize
Python API for Premiumize.me Torrent Cloud

## Usage

```python

from premiumize import Premiumize

# create a Premiumize object with default domain
p = Premiumize()

# set the credentials for API access
p.set_account('customerId', 'pin')

# list the torrents currently in your Torrent Cloud
for torrent in p.torrents():
  torrent.print_torrent()
  
# list the files and corresponding dowload links of each torrent
for torrent in p.torrents():
  for item in torrent.items():
    '{0}: {1}'.format(item.name, item.link)

```
