# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
#from GtkHelper.GenerativeUI.EntryRow import EntryRow

from gi.repository import Adw
from pathlib import Path

import os

# Import actions
from .actions.SimpleAction.SimpleAction import SimpleAction
from .actions.Mpd.Mpd import MpdAlbum
from .actions.Mpd.Mpd import MpdArtist
from .actions.Mpd.Mpd import MpdArtistAlbum
from .actions.Mpd.Mpd import MpdCover
from .actions.Mpd.Mpd import MpdProgress
from .actions.Mpd.Mpd import MpdSong

class MpdPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        # Register actions
        self.mpd_progress_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdProgress,
            action_id = "net_birdbrain_mpd::MpdProgress",
            action_name = "Show Progress",
        )
        self.add_action_holder(self.mpd_progress_holder)

        self.mpd_album_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdAlbum,
            action_id = "net_birdbrain_mpd::MpdAlbum",
            action_name = "Show Album",
        )
        self.add_action_holder(self.mpd_album_holder)

        self.mpd_artist_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdArtist,
            action_id = "net_birdbrain_mpd::MpdArtist",
            action_name = "Show Artist",
        )
        self.add_action_holder(self.mpd_artist_holder)

        self.mpd_artistalbum_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdArtistAlbum,
            action_id = "net_birdbrain_mpd::MpdArtistAlbum",
            action_name = "Show Artist and Album",
        )
        self.add_action_holder(self.mpd_artistalbum_holder)

        self.mpd_song_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdSong,
            action_id = "net_birdbrain_mpd::MpdSong",
            action_name = "Show Song",
        )
        self.add_action_holder(self.mpd_song_holder)

        self.mpd_cover_holder = ActionHolder(
            plugin_base = self,
            action_base = MpdCover,
            action_id = "net_birdbrain_mpd::MpdCover",
            action_name = "Show Cover",
        )
        self.add_action_holder(self.mpd_cover_holder)

        # Register plugin
        self.register(
            plugin_name = "mpd - Music Player Daemon Status",
            github_repo = "https://github.com/kda/MpdPluginForStreamController",
            plugin_version = "0.0.1",
            app_version = "1.5.0"
        )

    def get_settings_area(self):
        self._mpd_host_entry = Adw.EntryRow(
            title="MPD host",
        )
        self._mpd_port_entry = Adw.EntryRow(
            title="MPD port",
        )
        self._music_directory_entry = Adw.EntryRow(
            title="Music Directory",
        )

        settings = self.get_settings()
        if settings is not None:
            mpd_host = settings.setdefault('mpd_host', 'localhost')
            mpd_port = settings.setdefault('mpd_port', 6600)
            music_directory = settings.setdefault('music_directory', os.path.join(Path.home(), 'music'))

            self._mpd_host_entry.set_text(mpd_host)
            self._mpd_port_entry.set_text(str(mpd_port))
            self._music_directory_entry.set_text(music_directory)

        self._mpd_host_entry.connect("notify::text", self._on_mpd_host_change)
        self._mpd_port_entry.connect("notify::text", self._on_mpd_port_change)
        self._music_directory_entry.connect("notify::text", self._on_music_directory_change)

        pref_group = Adw.PreferencesGroup()
        pref_group.add(self._mpd_host_entry)
        pref_group.add(self._mpd_port_entry)
        pref_group.add(self._music_directory_entry)
        return pref_group


    def _on_mpd_host_change(self, entry_row, pspec):
        settings = self.get_settings()
        settings['mpd_host'] = entry_row.get_text()
        self.set_settings(settings)
        self.notify_actions_of_setting_changes(settings)

    def _on_mpd_port_change(self, entry_row, pspec):
        settings = self.get_settings()
        settings['mpd_port'] = int(entry_row.get_text())
        self.set_settings(settings)
        self.notify_actions_of_setting_changes(settings)

    def _on_music_directory_change(self, entry_row, pspec):
        settings = self.get_settings()
        settings['music_directory'] = entry_row.get_text()
        self.set_settings(settings)
        self.notify_actions_of_setting_changes(settings)

    def notify_actions_of_setting_changes(self, new_settings):
        MpdAlbum.global_settings_changed(new_settings)
        MpdArtist.global_settings_changed(new_settings)
        MpdArtistAlbum.global_settings_changed(new_settings)
        MpdCover.global_settings_changed(new_settings)
        MpdProgress.global_settings_changed(new_settings)
        MpdSong.global_settings_changed(new_settings)
