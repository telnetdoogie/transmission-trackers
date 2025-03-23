# telnetdoogie -  https://github.com/telnetdoogie/transmission-trackers
import os, time

from torrents_updater import TorrentUpdater
from trackers_updater import TrackerUpdater


class App:

    def __init__(self):

        # defaults
        self.user = "transmission"
        self.password = "password"
        self.host = "transmission"
        self.port: int = 9091
        self.trackers_list = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"
        self.period: int = 120
        self.tracker_expiration_time: int = 28800  # 8 hours
        self.is_debug = False

        self.override_params_from_env()

        self.tracker_updater: TrackerUpdater = TrackerUpdater(url=self.trackers_list,
                                                              expiration_time=self.tracker_expiration_time,
                                                              debug=self.debug)
        self.torrent_updater: TorrentUpdater = TorrentUpdater(user=self.user, password=self.password, host=self.host,
                                                              port=self.port, period=self.period, debug=self.debug,
                                                              get_trackers=self.tracker_updater.get_trackers)

    def main(self):

        # Start the tracker updater
        self.tracker_updater.start()

        print("Waiting for the tracker updater to successfully load trackers...")
        self.tracker_updater.initial_load_event.wait(timeout=300)  # Wait until trackers are loaded

        if not self.tracker_updater.initial_load_event.is_set():
            print("Failed to load trackers within the timeout period. Exiting.")
            return

        print("Trackers loaded.")

        # Once the trackers are loaded, start the torrent updater
        self.torrent_updater.main()

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
            "DEBUG": ("is_debug", bool),
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
                    print(f"Setting {env_var} to {converted_value}{'s' if env_var in seconds_variables else ''}")
                except ValueError:
                    print(f"{env_var} passed was not a valid {attr_type.__name__}")
                    exit(1)

    def debug(self, message: str):
        if self.is_debug:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] DEBUG: {message}")


if __name__ == "__main__":
    app = App()
    app.main()
