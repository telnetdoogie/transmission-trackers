# transmission-trackers

[![CodeFactor](https://www.codefactor.io/repository/github/telnetdoogie/transmission-trackers/badge/main)](https://www.codefactor.io/repository/github/telnetdoogie/transmission-trackers/overview/main)

This minimal-config docker image will run alongside your transmission installation, check for active non-private torrents, and update their trackers (add additional trackers) using a user-defined tracker-list such as the ones provided by [@ngosang](https://github.com/ngosang) at https://github.com/ngosang/trackerslist or [@corralpeltzer](https://github.com/CorralPeltzer)'s [newTrackOn Lists](https://newtrackon.com/)

The tracker list will only be downloaded every 8 hours by default, but this frequency can be modified by environment variables.

Torrents are checked every 2 minutes (this can also be customized by environment variables)

If a torrent already has the additional trackers present, no changes will be made. This app will also not make any tracker modifications to torrents flagged as private.

Please note this is a v1 project. While it's been tested on my own setup, there may be issues and configurations that have not been fully tested. 
Report issues in [Issues](https://github.com/telnetdoogie/transmission-trackers/issues)

## transmission-trackers in action

<p align="center" width="100%">
<video src="https://github.com/user-attachments/assets/5c62b66b-389b-4e1d-90af-c1eecbc8c309" width="80%" controls></video>
</p>


## Running from `docker` command-line

Add additional environment variables as needed; see the table below for details.

### _with (default) newtrackon stable list_
```console
docker run --rm --name transmission-trackers \
    -e TRANSMISSION_HOST=transmission \
    telnetdoogie/transmission-trackers:latest
```

### _with ngosang's best trackers list_
```console
docker run --rm --name transmission-trackers \
    -e TRANSMISSION_HOST=transmission \
    -e TRACKERS_LIST=https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best_ip.txt \
    telnetdoogie/transmission-trackers:latest
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
      TRACKERS_LIST: https://newtrackon.com/api/98?min_age_days=5 # use any URL that returns a line-separated list of trackers
    restart: unless-stopped
```

## Environment Variables:

See the table of Environment variables you can add below to either `docker-compose.yml` or the `docker run` command.

You can set these as needed to override the defaults. If the defaults are acceptable, there is no need to add the variables.

| Variable               | Description                                                                           | Default Value                       |
|------------------------|---------------------------------------------------------------------------------------|-------------------------------------|
| `TRANSMISSION_HOST`    | IP or hostname of transmission host                                                   | `transmission`                      |
| `TRANSMISSION_PORT`    | Port of transmission host                                                             | `9091`                              |
| `TRACKERS_LIST`        | URL for tracker list                                                                  | `https://newtrackon.com/api/stable` |
| `TRANSMISSION_USER`    | Username for transmission. Ignore if no auth needed.                                  | `transmission`                      |
| `TRANSMISSION_PASS`    | Password for transmission. Ignore if no auth needed.                                  | `password`                          |
| `TORRENT_CHECK_PERIOD` | How frequent (in seconds) we'll check for active torrents                             | `120` (2 minutes)                   |
| `TRACKER_EXPIRATION`   | How long downloaded tracker list will kept (in seconds) before downloading the latest | `28800` (8 hours)                   |
| `DEBUG`                | Enables more verbose output for tracker and torrent updates                           | `False`                             |

## Which List Should I Use?

You can use any URL that returns a line-separated list of trackers, so find your favorite list and use that one. I have not added support to combine lists, nor currently will this remove trackers that fall off the lists as they're updated, but if there's demand for that, it could be added. 

In the case of the newtrackon list, you can use the API as you see fit:
- `https://newtrackon.com/api/stable` - stable list
- `https://newtrackon.com/api/98?min_age_days=5` - list with 98%+ uptime, and 5+ tracker age in days
