# transmission-trackers

This minimal-config docker image will run against your transmission installation, check for active torrents, and update their trackers using a user-defined tracker-list such as the ones provided by @ngosang at https://github.com/ngosang/trackerslist.

The tracker list will only be downloaded every 8 hours by default (the example list only changes once per day on average) but this frequency can be modified by environment variables.

Torrents are checked every 2 minutes (this can also be customized by environment variables)

If a torrent already has the additional trackers present, no changes will be made.

Please note this is a v1 project. While it's been tested on my own setup, there may be issues and configurations that have not been fully tested. 
Report issues in [Issues](https://github.com/telnetdoogie/transmission-trackers/issues)

## Running from `docker` command-line

```console
docker run --rm --name transmission-trackers \
    -e TRANSMISSION_HOST=transmission \
    -e TRACKERS_LIST=https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best_ip.txt \
    telnetdoogie/docker-par2cmdline
```

## Running from `docker-compose`

Create a docker-compose.yml file as below (and customize with environment entries from the table below if you need) and start with `docker-compose up -d`
```yml
services:
  transmission-trackers:
    container_name: transmission-trackers
    image: telnetdoogie/transmission-trackers:latest
    environment:
      TRANSMISSION_HOST: 192.168.1.225  # ip or name of your transmission instance
      TRANSMISSION_PORT: 9092           # no need for this setting if transmission is running on the default port 
    restart: unless-stopped
```

## Environment Variables:

See the table of Environment variables you can add below to either `docker-compose.yml` or the `docker run` command.

You can set these as needed to override the defaults. If the defaults are acceptable, there is no need to add the variables.

| Variable               | Description                                                                           | Default Value                                                                     |
|------------------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `TRANSMISSION_HOST`    | IP or hostname of transmission host                                                   | `transmission`                                                                    |
| `TRANSMISSION_PORT`    | Port of transmission host                                                             | `9091`                                                                            |
| `TRACKERS_LIST`        | URL for tracker list                                                                  | `https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt` |
| `TRANSMISSION_USER`    | Username for transmission. Ignore if no auth needed.                                  | `transmission`                                                                    |
| `TRANSMISSION_PASS`    | Password for transmission. Ignore if no auth needed.                                  | `password`                                                                        |
| `TORRENT_CHECK_PERIOD` | How frequent (in seconds) we'll check for active torrents                             | `120` (2 minutes)                                                                 |
| `TRACKER_EXPIRATION`   | How long downloaded tracker list will kept (in seconds) before downloading the latest | `28800` (8 hours)                                                                 |

