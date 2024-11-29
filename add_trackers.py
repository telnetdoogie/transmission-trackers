import os
import threading
import time
import transmission_rpc

import requests
from transmission_rpc import Torrent


class TrackerUpdater:
    def __init__(self, url, expiration_time: float):
        print("TrackerUpdater Initializing...")
        self.url = url
        self.list_expiration_time = expiration_time
        self._running = True
        self.trackers = None
        self.trackers_timestamp = None
        self.lock = threading.Lock()
        self.initial_load_event = threading.Event()

    def start(self):
        thread = threading.Thread(target=self.__run, daemon=True)
        thread.start()

    def stop(self):
        self._running = False

    def __run(self):
        while self._running:
            current_time = time.time()
            if (self.trackers is None or self.trackers_timestamp is None) or (
                    (current_time - self.trackers_timestamp) > self.list_expiration_time):
                self.__load_trackers()
            time.sleep(60 * 5)

    def __load_trackers(self):
        with self.lock:
            try:
                response = requests.get(self.url)
                response.raise_for_status()
                self.trackers = [line for line in response.text.splitlines() if line.strip()]
                current_time = time.time()
                self.trackers_timestamp = current_time
                print(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Trackers loaded from {self.url}:")
                for index, tracker in enumerate(self.trackers):
                    print(f"  {index:02} : {tracker}")
                self.initial_load_event.set()
            except requests.RequestException as e:
                print(f"Error fetching trackers from {self.url}: {e}")
                return

    def get_trackers(self):
        return self.trackers


class TorrentUpdater:

    def __init__(self):

        print("TorrentUpdater Initializing...")
        # defaults
        self.user = "transmission"
        self.password = "password"
        self.host = "transmission"
        self.port: int = 9091
        self.trackers_list = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"
        self.period: float = 120
        self.tracker_expiration_time: float = 28800  # 8 hours

        if os.getenv("TRANSMISSION_HOST"):
            self.host = os.getenv("TRANSMISSION_HOST")
            print(f"Setting HOST to {self.host}")

        if os.getenv("TRANSMISSION_PORT"):
            try:
                self.port = int(os.getenv("TRANSMISSION_PORT"))
            except ValueError:
                print("TRANSMISSION_PORT passed was not a number")
                exit(1)
            print(f"Setting TRANSMISSION_PORT to {self.port}")

        if os.getenv("TRACKERS_LIST"):
            self.trackers_list = os.getenv("TRACKERS_LIST")
            print(f"Setting TRACKERS_LIST to {self.trackers_list}")

        if os.getenv("TRANSMISSION_USER"):
            self.user = os.getenv("TRANSMISSION_USER")
            print(f"Setting TRANSMISSION_USER to {self.user}")

        if os.getenv("TRANSMISSION_PASS"):
            self.password = os.getenv("TRANSMISSION_PASS")
            print(f"Setting TRANSMISSION_PASS to {self.password}")

        if os.getenv("TORRENT_CHECK_PERIOD"):
            try:
                self.period = float(os.getenv("TORRENT_CHECK_PERIOD"))
            except ValueError:
                print("TORRENT_CHECK_PERIOD passed was not a number")
                exit(1)
            print(f"Setting TORRENT_CHECK_PERIOD to {round(self.period)}s")

        if os.getenv("TRACKER_EXPIRATION"):
            try:
                self.tracker_expiration_time = float(os.getenv("TRACKER_EXPIRATION"))
            except ValueError:
                print("TRACKER_EXPIRATION passed was not a number")
                exit(1)
            print(f"Setting TRACKER_EXPIRATION to {round(self.tracker_expiration_time)}s")

        self.updater = TrackerUpdater(url=self.trackers_list, expiration_time=self.tracker_expiration_time)
        self.updater.start()

    def update_trackers(self, torrent: Torrent):
        tc = transmission_rpc.Client(username=self.user, password=self.password, host=self.host, port=self.port)
        current_trackers = tc.get_torrent(torrent_id=torrent.id).tracker_list
        new_trackers = self.updater.get_trackers()
        # Make a union of current and new trackers
        all_trackers = list(set(new_trackers) | set(current_trackers))
        if sorted(current_trackers) != sorted(all_trackers):
            print(f"Updating trackers for {torrent.name}")
            print(f" - current trackers ({len(current_trackers)})")
            print(f" - new trackers ({len(new_trackers)}):")
            print(f" - combined list ({len(all_trackers)}):")
            tc.change_torrent(ids=torrent.id, tracker_list=[all_trackers])
            print(f" - Trackers updated for {torrent.name}")

    def get_torrents(self):
        try:
            tc = transmission_rpc.Client(username=self.user, password=self.password, host=self.host, port=self.port)
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
        print(f"Watching for new torrents every {round(self.period)} seconds...")
        while True:
            torrents: list[Torrent] = self.get_torrents()
            print(f"Checking active torrents ({len(torrents)})")
            for torrent in torrents:
                self.update_trackers(torrent)
            time.sleep(self.period)


if __name__ == "__main__":
    app = TorrentUpdater()
    app.main()
