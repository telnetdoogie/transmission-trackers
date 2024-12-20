# telnetdoogie -  https://github.com/telnetdoogie/transmission-trackers
import os
import time

from transmission_rpc import Torrent, Client

from trackers_updater import TrackerUpdater


class TorrentUpdater:

    def __init__(self):

        print("TorrentUpdater Initializing...")
        # defaults
        self.user = "transmission"
        self.password = "password"
        self.host = "transmission"
        self.port: int = 9091
        self.trackers_list = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"
        self.period: int = 120
        self.tracker_expiration_time: int = 28800  # 8 hours

        self.override_params_from_env()

        self.updater = TrackerUpdater(url=self.trackers_list, expiration_time=self.tracker_expiration_time)
        self.updater.start()

    def override_params_from_env(self):
        # Map environment variable names to attributes
        env_params = {
            "TRANSMISSION_HOST": ("host", str),
            "TRANSMISSION_PORT": ("port", int),
            "TRACKERS_LIST": ("trackers_list", str),
            "TRANSMISSION_USER": ("user", str),
            "TRANSMISSION_PASS": ("password", str),
            "TORRENT_CHECK_PERIOD": ("period", int),
            "TRACKER_EXPIRATION": ("tracker_expiration_time", int),
        }
        # Seconds-based environment variables
        seconds_variables = {"TORRENT_CHECK_PERIOD", "TRACKER_EXPIRATION"}

        # Iterate over the mapping
        for env_var, (attr, attr_type) in env_params.items():
            value = os.getenv(env_var)
            if value:
                try:
                    # Convert values to the correct type
                    converted_value = attr_type(value)
                    setattr(self, attr, converted_value)

                    if env_var in seconds_variables:
                        print(f"Setting {env_var} to {converted_value}s")
                    else:
                        print(f"Setting {env_var} to {converted_value}")
                except ValueError:
                    print(f"{env_var} passed was not a valid {attr_type.__name__}")
                    exit(1)

    def update_trackers(self, torrent: Torrent):
        try:
            tc = Client(username=self.user, password=self.password, host=self.host, port=self.port)
            current_trackers = tc.get_torrent(torrent_id=torrent.hashString).tracker_list
            new_trackers = self.updater.get_trackers()
            # Make a union of current and new trackers
            all_trackers = list(set(new_trackers) | set(current_trackers))
            if sorted(current_trackers) != sorted(all_trackers):
                print(f'Updating trackers for "{torrent.name}"')
                print(f" - {len(current_trackers)} current trackers")
                print(f" - {len(all_trackers)} trackers after update")
                tc.change_torrent(ids=torrent.hashString, tracker_list=[all_trackers])
                print(f' - Trackers updated for "{torrent.name}"')
        except Exception as e:
            print(f"An error occurred updating trackers: {e}")
        return

    def get_torrents(self):
        try:
            tc = Client(username=self.user, password=self.password, host=self.host, port=self.port)
            torrents = tc.get_torrents()
            return torrents
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def main(self):
        print("Waiting for the tracker updater to successfully load trackers...")
        self.updater.initial_load_event.wait(timeout=300)  # Wait until trackers are loaded

        if not self.updater.initial_load_event.is_set():
            print("Failed to load trackers within the timeout period. Exiting.")
            return

        print("Trackers loaded.")
        self.check_and_update_torrents()

    def check_and_update_torrents(self):
        print(f"Watching for new torrents every {self.period} seconds...")
        torrent_names = []
        while True:
            torrents: list[Torrent] = self.get_torrents()

            # put active torrent names in a list
            new_torrent_names = sorted(torrent.name for torrent in torrents)

            # summarize the additions / deletions for output
            if new_torrent_names != torrent_names:

                added_torrents = set(new_torrent_names) - set(torrent_names)
                removed_torrents = set(torrent_names) - set(new_torrent_names)

                print(f"Active torrents have changed ({len(torrents)} active)")
                for name in added_torrents:
                    print(f' - New torrent: "{name}"')
                for name in removed_torrents:
                    print(f' - Torrent removed: "{name}"')
                torrent_names = new_torrent_names

            for torrent in torrents:
                # don't change anything in private torrents
                if not torrent.is_private:
                    self.update_trackers(torrent)
            time.sleep(self.period)



