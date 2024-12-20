# telnetdoogie -  https://github.com/telnetdoogie/transmission-trackers
import threading
import time

import requests


class TrackerUpdater:
    def __init__(self, url, expiration_time: int):
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

    def __print_trackers(self):
        current_time = time.time()
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Trackers loaded from {self.url}")
        for index, tracker in enumerate(self.trackers):
            print(f"  {index:02} : {tracker}")

    def __load_trackers(self):
        with self.lock:
            try:
                response = requests.get(self.url)
                response.raise_for_status()
                trackers = [line for line in response.text.splitlines() if line.strip()]
                current_time = time.time()
                if self.trackers is None:
                    self.trackers = trackers
                    self.__print_trackers()
                else:
                    if self.trackers != trackers:
                        # trackers have changed since last download
                        self.trackers = trackers
                        self.__print_trackers()
                    else:
                        print(
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}: Trackers from {self.url} have not changed")
                self.trackers_timestamp = current_time
                self.initial_load_event.set()
            except requests.RequestException as e:
                print(f"Error fetching trackers from {self.url}: {e}")
                return

    def get_trackers(self):
        return self.trackers
