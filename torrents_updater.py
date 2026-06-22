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


    def update_trackers_for_torrent(self, torrent: Torrent, client: Client):

        try:
            current_trackers = client.get_torrent(torrent_id=torrent.hashString).tracker_list
            original_current_trackers = list(current_trackers)  # Keep original for comparison
            new_trackers_tiers = self.get_trackers()

            if not new_trackers_tiers:
                return

            # Flatten new tiers to get all available trackers
            all_new_trackers = [t for tier in new_trackers_tiers for t in tier]

            # Build updated tiers preserving tier structure
            updated_tiers = []
            for tier in new_trackers_tiers:
                tier_trackers = list(tier)  # Start with trackers from this tier
                # Add any current trackers not in the new lists to this tier
                for ct in current_trackers:
                    if ct not in all_new_trackers and ct not in tier_trackers:
                        tier_trackers.append(ct)
                if tier_trackers:
                    updated_tiers.append(tier_trackers)

            # Add any remaining current trackers to the last tier or as a new tier
            if current_trackers:
                remaining = [ct for ct in current_trackers if ct not in all_new_trackers]
                if remaining:
                    if updated_tiers:
                        updated_tiers[-1].extend(remaining)
                    else:
                        updated_tiers.append(remaining)

            # Check if changes are needed
            final_trackers_flat = [t for tier in updated_tiers for t in tier]
            if sorted(original_current_trackers) != sorted(final_trackers_flat):
                print(f'Updating trackers for "{torrent.name}"')
                print(f" - {len(original_current_trackers)} current trackers")
                print(f" - {len(updated_tiers)} tiers after update")
                client.change_torrent(ids=torrent.hashString, tracker_list=updated_tiers)
                print(f' - Trackers updated for "{torrent.name}"')
        except Exception as e:
            print(f"An error occurred updating trackers: {e}")
            self.debug(torrent_info(torrent))

    def get_torrents(self, client: Client):
        try:
            torrents = client.get_torrents()
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
            self.debug(f"  - skipping torrent (not eligible): {torrent.hashString}")
            return False
        return True

    def check_and_update_torrents(self):
        print(f"Watching for new active torrents every {self.period} seconds...")
        torrent_names: list[str] = []
        client = Client(username=self.user, password=self.password, host=self.host, port=self.port)
        while True:
            # get the active torrents
            torrents: list[Torrent] = self.get_torrents(client=client)
            # check for eligible torrents
            eligible_torrents = [torrent for torrent in torrents if self.is_torrent_qualified_for_update(torrent)]
            # put eligible torrent names in a list
            new_eligible_torrent_names = get_sorted_torrent_names(eligible_torrents)
            # summarize the additions / deletions for output
            if new_eligible_torrent_names != torrent_names:
                log_torrent_changes(torrent_names, new_eligible_torrent_names, len(eligible_torrents))
                torrent_names = new_eligible_torrent_names
            self.update_torrents(eligible_torrents, client=client)
            for _ in range(self.period):
                time.sleep(1)

    def update_torrents(self, torrents: list[Torrent], client: Client):
        for torrent in torrents:
            self.update_trackers_for_torrent(torrent, client=client)
