# telnetdoogie -  https://github.com/telnetdoogie/transmission-trackers
import json
import time

from transmission_rpc import Torrent, Client


def log_torrent_changes(old_name_list: list[str], new_name_list: list[str], active_count: int):
    added_torrents = set(new_name_list) - set(old_name_list)
    removed_torrents = set(old_name_list) - set(new_name_list)
    print(f"Active torrents have changed ({active_count} active)")
    for name in added_torrents:
        print(f' - New torrent: "{name}"')
    for name in removed_torrents:
        print(f' - Torrent removed: "{name}"')


def get_sorted_torrent_names(torrents: list[Torrent]):
    return sorted(torrent.name for torrent in torrents)


def torrent_info(torrent: Torrent):
    json_output = json.dumps(torrent.__dict__, indent=4)
    return json_output


class TorrentUpdater:

    def __init__(self, user: str, password: str, host: str, port: int, period: int, debug, get_trackers):

        print("TorrentUpdater Initializing...")
        # defaults
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.period = period
        self.debug = debug
        self.get_trackers = get_trackers

    def update_trackers_for_torrent(self, torrent: Torrent):

        try:
            tc = Client(username=self.user, password=self.password, host=self.host, port=self.port)
            current_trackers = tc.get_torrent(torrent_id=torrent.hashString).tracker_list
            new_trackers = self.get_trackers()
            # Make a union of current and new trackers
            all_trackers = list(set(new_trackers) | set(current_trackers))
            if sorted(current_trackers) != sorted(all_trackers):
                print(f'Updating trackers for "{torrent.name}"')
                print(f" - {len(current_trackers)} current trackers")
                print(f" - {len(all_trackers)} trackers after update")
                tc.change_torrent(ids=torrent.hashString, tracker_list=[[t] for t in all_trackers])
                print(f' - Trackers updated for "{torrent.name}"')
        except Exception as e:
            print(f"An error occurred updating trackers: {e}")
            self.debug(torrent_info(torrent))

    def get_torrents(self):
        try:
            tc = Client(username=self.user, password=self.password, host=self.host, port=self.port)
            torrents = tc.get_torrents()
            return torrents
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def main(self):
        print("Checking and Updating Torrents...")
        self.check_and_update_torrents()

    def is_torrent_qualified_for_update(self, torrent: Torrent):
        # Do not update private torrents or unstarted torrents
        if torrent.is_private or torrent.activity_date < torrent.added_date:
            self.debug(f"  - skipping torrent (not eligible): {torrent.id}")
            return False
        return True

    def check_and_update_torrents(self):
        print(f"Watching for new active torrents every {self.period} seconds...")
        torrent_names: list[str] = []
        while True:
            # get the active torrents
            torrents: list[Torrent] = self.get_torrents()
            # check for eligible torrents
            eligible_torrents = [torrent for torrent in torrents if self.is_torrent_qualified_for_update(torrent)]
            # put eligible torrent names in a list
            new_eligible_torrent_names = get_sorted_torrent_names(eligible_torrents)
            # summarize the additions / deletions for output
            if new_eligible_torrent_names != torrent_names:
                log_torrent_changes(torrent_names, new_eligible_torrent_names, len(eligible_torrents))
                torrent_names = new_eligible_torrent_names
            self.update_torrents(eligible_torrents)
            time.sleep(self.period)

    def update_torrents(self, torrents: list[Torrent]):
        for torrent in torrents:
            self.update_trackers_for_torrent(torrent)
