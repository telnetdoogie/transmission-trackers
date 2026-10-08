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
        self.trackers_lists: list[str] = ["https://newtrackon.com/api/stable"]
        self.tracker_priority: list[int] = None  # None means natural order
        self.period: int = 120
        self.tracker_expiration_time: int = 28800  # 8 hours
        self.is_debug = False

        self.override_params_from_env()

        # Build tracker URLs based on priority
        urls = self.__build_ordered_urls()

        self.tracker_updater: TrackerUpdater = TrackerUpdater(urls=urls,
                                                              expiration_time=self.tracker_expiration_time,
                                                              debug=self.debug)
        self.torrent_updater: TorrentUpdater = TorrentUpdater(user=self.user, password=self.password, host=self.host,
                                                              port=self.port, period=self.period, debug=self.debug,
                                                              get_trackers=self.tracker_updater.get_trackers)

    def __build_ordered_urls(self) -> list[str]:
        """Build ordered list of tracker URLs based on priority setting."""
        if self.tracker_priority is None:
            return self.trackers_lists

        # Reorder URLs based on priority
        ordered = []
        for p in self.tracker_priority:
            if 0 <= p < len(self.trackers_lists):
                ordered.append(self.trackers_lists[p])
        # Append any remaining URLs not in priority list
        for i, url in enumerate(self.trackers_lists):
            if i not in self.tracker_priority and url not in ordered:
                ordered.append(url)
        return ordered

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
            "TRACKER_LISTS": ("tracker_lists", list[str]),
            "TRACKER_PRIORITY": ("tracker_priority", list[int]),
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
            if value is not None:
                try:
                    # Convert values to the correct type
                    if attr_type is bool:
                        converted_value = value.lower() in ("true", "yes", "1")
                    elif attr_type is list[str]:
                        converted_value = [v.strip() for v in value.split("|") if v.strip()]
                    elif attr_type is list[int]:
                        converted_value = [int(v.strip()) for v in value.split(",") if v.strip()]
                    else:
                        converted_value = attr_type(value)
                    setattr(self, attr, converted_value)
                    print(f"Setting {env_var} to {converted_value}{'s' if env_var in seconds_variables else ''}")
                except ValueError:
                    print(f"{env_var} passed was not a valid {attr_type.__name__}")
                    exit(1)

        # Handle backward compatibility: TRACKERS_LIST -> tracker_lists
        if not hasattr(self, 'tracker_lists') or not self.tracker_lists:
            if hasattr(self, 'trackers_list') and self.trackers_list:
                self.tracker_lists = [self.trackers_list]

    def debug(self, message: str):
        if self.is_debug:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] DEBUG: {message}")



def main():
    app = App()
    try:
        app.main()
    except KeyboardInterrupt:
        print("Exiting...")
        app.tracker_updater.stop()

if __name__ == "__main__":
    main()
