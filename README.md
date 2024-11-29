
## ENV Variables:

You can set these as needed to override the defaults.

| Variable               | Description                                                                           | Default Value                                                                     |
|------------------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `TRANSMISSION_HOST`    | IP or hostname of transmission host                                                   | `transmission`                                                                    |
| `TRANSMISSION_PORT`    | Port of transmission host                                                             | `9091`                                                                            |
| `TRACKERS_LIST`        | URL for tracker list                                                                  | `https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt` |
| `TRANSMISSION_USER`    | Username for transmission. Ignore if no auth needed.                                  | `transmission`                                                                    |
| `TRANSMISSION_PASS`    | Password for transmission. Ignore if no auth needed.                                  | `password`                                                                        |
| `TORRENT_CHECK_PERIOD` | How frequent (in seconds) we'll check for active torrents                             | `120` (2 minutes)                                                                 |
| `TRACKER_EXPIRATION`   | How long downloaded tracker list will kept (in seconds) before downloading the latest | `28800` (8 hours)                                                                 |

This is a v1 project. Report issues in [Issues](https://github.com/telnetdoogie/transmission-trackers/issues)