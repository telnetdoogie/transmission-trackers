# telnetdoogie -  https://github.com/telnetdoogie/transmission-trackers
import threading
import time

import requests


class TrackerUpdater:
    def __init__(self, urls: list[str], expiration_time: int, debug):
        print("TrackerUpdater Initializing...")
        self.urls = urls
        self.list_expiration_time = expiration_time
        self._running = True
        self.trackers_tiers: list[list[str]] = None
        self.trackers_timestamp = None
        self.lock = threading.Lock()
        self.initial_load_event = threading.Event()
        self.debug = debug

    def start(self):
        thread = threading.Thread(target=self.__run, daemon=True)
        thread.start()

    def stop(self):
        self._running = False

    def __run(self):
        while self._running:
            current_time = time.time()
            if (self.trackers_tiers is None or self.trackers_timestamp is None) or (
                    (current_time - self.trackers_timestamp) > self.list_expiration_time):
                self.__load_trackers()
            time.sleep(60 * 5)

    def __print_trackers(self):
        current_time = time.time()
        for tier_idx, trackers in enumerate(self.trackers_tiers):
            self.debug(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Tier {tier_idx} trackers:")
            for index, tracker in enumerate(trackers):
                self.debug(f"    {index:02} : {tracker}")

    def __load_trackers(self):
        with self.lock:
            try:
                all_tiers: list[list[str]] = []
                for url in self.urls:
                    response = requests.get(url)
                    response.raise_for_status()
                    trackers = [line for line in response.text.splitlines() if line.strip()]
                    if trackers:
                        all_tiers.append(trackers)

                current_time = time.time()
                if self.trackers_tiers is None or self.trackers_tiers != all_tiers:
                    print(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Tracker tiers updated from {len(self.urls)} source(s)")
                    self.trackers_tiers = all_tiers
                    self.__print_trackers()
                else:
                    print(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Tracker tiers have not changed")
                self.trackers_timestamp = current_time
                self.initial_load_event.set()
            except requests.RequestException as e:
                print(f"Error fetching trackers: {e}")
                return

    def get_trackers(self):
        return self.trackers_tiers
