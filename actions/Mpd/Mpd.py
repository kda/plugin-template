# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input

from loguru import logger as log

# Import python modules
import os
import time

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from PIL import Image, ImageDraw
from mpd import MPDClient

class MpdConnection:
    _instance = None
    _mpdc = None
    _previousRunTime = 0.0
    _previousRetval = (None, None)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host, port):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._host = host
        self._port = port

    @classmethod
    def reset_connection(cls, host, port):
        if cls._instance is not None:
            cls._instance._mpdc = None
            cls._instance._host = host
            cls._instance._port = port

    def fetchState(self) -> (dict[str, str], dict[str, str]):
        if (time.time() - self._previousRunTime) < 0.9:
            return self._previousRetval
        self._previousRunTime = time.time()
        if self._mpdc is None:
            self._mpdc = MPDClient()
            try:
                self._mpdc.connect(self._host, self._port)
            except Exception as err:
                print(f'Unexpected {err=}, {type(err)=}')
                self._mpdc = None
                return self._previousRetval

        try:
            mpdcStatus = self._mpdc.status()
            #print(f'mpdcStatus: {mpdcStatus}')
            mpdcCurrentSong = self._mpdc.currentsong()
            #print(f'mpdcCurrentSong: {mpdcCurrentSong}')
        except Exception as err:
            print(f'Unexpected {err=}, {type(err)=}')
            self._mpdc = None
            return self._previousRetval

        self._previousRetval = (mpdcStatus, mpdcCurrentSong)
        return self._previousRetval

class MpdCore(ActionCore):
    _instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instances.append(self)
        settings = self.plugin_base.get_settings()
        self._mpdcon = MpdConnection(settings['mpd_host'], settings['mpd_port'])
        image_format = self.deck_controller.deck.key_image_format()
        (self._iconWidth, self._iconHeight) = image_format['size']
        self._state = None
        self._lastUpdate = 0.0

    def on_tick(self) -> None:
        self.on_ready()

    def on_ready(self):
        pass

    def on_remove(self):
        self._state = None
        if self in self._instances:
            self._instances.remove(self)
        super().on_remove()

    @classmethod
    def global_settings_changed(cls, new_settings):
        MpdConnection.reset_connection(new_settings['mpd_host'], new_settings['mpd_port'])
        for instance in list(cls._instances):
            instance.apply_new_settings(new_settings)

#    def apply_new_settings(self, settings):
#        pass

#    def on_update(self) -> None:
#        self._state = None
#        super().on_update()

    def _prep_image(self) -> (Image, ImageDraw):
        image = Image.new("RGB", (self._iconWidth, self._iconHeight), "black")
        return (image, ImageDraw.Draw(image))

    def _render_image(self, content) -> None:
        if content == self._state and (time.time() - self._lastUpdate) < 10.0:
            #log.info(f'content: {content} self._state: {self._state}')
            return
        self._state = content

        (image, draw) = self._prep_image()
        (width, height) = (self._iconWidth, self._iconHeight)
        allLines = []
        for valueLine in content.splitlines():
            textWidth = draw.textlength(valueLine)
            lines = []
            if textWidth > width:
                valuePieces = valueLine.split(' ')
                valuePieceIndex = 0
                while valuePieceIndex < len(valuePieces):
                    line = valuePieces[valuePieceIndex]
                    valuePieceIndex += 1
                    textWidth = draw.textlength(line)
                    if textWidth > width:
                        lines.append(line)
                        continue
                    while textWidth < width:
                        if valuePieceIndex >= len(valuePieces):
                            lines.append(line)
                            line = ''
                            break
                        if len(line) > 0:
                            line += ' '
                        line += valuePieces[valuePieceIndex]
                        valuePieceIndex += 1
                        textWidth = draw.textlength(line)
                    if len(line) > 0:
                        line = line[:line.rfind(' ')]
                        valuePieceIndex -= 1
                        lines.append(line)
                normalizedValue = '\n'.join(lines)
            else:
                normalizedValue = valueLine
            allLines.append(normalizedValue)
        allLinesMerged = '\n'.join(allLines)
        #print(f'allLinesMerged: {allLinesMerged}')
        draw.text((width/2, height/2), text=allLinesMerged, fill='white', anchor='mm', align='center')
        #log.info(f'rendered: content: {content}')
        self.set_media(image=image)
        self._lastUpdate = time.time()

class MpdProgress(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def on_ready(self) -> None:
        (mpdcStatus, _) = self._mpdcon.fetchState()
        state = '???'
        if mpdcStatus is not None:
            if set(['elapsed', 'duration', 'song', 'playlistlength']).issubset(mpdcStatus):
                elapsedMinutes = int(float(mpdcStatus["elapsed"]) / 60)
                elapsedSeconds = int(float(mpdcStatus["elapsed"]) % 60)
                durationMinutes = int(float(mpdcStatus["duration"]) / 60)
                durationSeconds = int(float(mpdcStatus["duration"]) % 60)
                percent = int((float(mpdcStatus["elapsed"]) * 100) / float(mpdcStatus["duration"]))
                songIndex = int(mpdcStatus['song']) + 1
                playlistLength = int(mpdcStatus['playlistlength'])
                state = '{}:{:>02}\n{}:{:>02}\n{}%\n{} / {}'.format(elapsedMinutes, elapsedSeconds, durationMinutes, durationSeconds, percent, songIndex, playlistLength)
            elif 'state' in mpdcStatus:
                state = f'{mpdcStatus["state"]}'

        if state == self._state:
            return

        (image, draw) = self._prep_image()
        draw.text((self._iconWidth/2, self._iconHeight/2), text=state, fill='white', anchor='mm', align='center')
        self.set_media(image=image)
        self._state = state

class MpdAlbum(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        (_, mpdcCurrentSong) = self._mpdcon.fetchState()
        value = 'album'
        if mpdcCurrentSong is not None and 'album' in mpdcCurrentSong:
            value = mpdcCurrentSong["album"]
        self._render_image(value)

class MpdArtist(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        (_, mpdcCurrentSong) = self._mpdcon.fetchState()
        value = 'artist'
        if mpdcCurrentSong is not None and 'artist' in mpdcCurrentSong:
            value = mpdcCurrentSong["artist"]
        self._render_image(value)

class MpdArtistAlbum(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        (_, mpdcCurrentSong) = self._mpdcon.fetchState()
        value = 'artist\n\nalbum'
        if mpdcCurrentSong is not None and set(['artist', 'album']).issubset(mpdcCurrentSong):
            value = f'{mpdcCurrentSong["artist"]}\n\n{mpdcCurrentSong["album"]}'
        self._render_image(value)

class MpdSong(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        (_, mpdcCurrentSong) = self._mpdcon.fetchState()
        value = 'song'
        if mpdcCurrentSong is not None and set(['track', 'title']).issubset(mpdcCurrentSong):
            value = f'{mpdcCurrentSong["track"]}\n{mpdcCurrentSong["title"]}'
        self._render_image(value)

class MpdCover(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = self.plugin_base.get_settings()
        self._music_directory = settings['music_directory']

    def on_ready(self) -> None:
        (_, mpdcCurrentSong) = self._mpdcon.fetchState()
        path = ''
        if mpdcCurrentSong is not None and 'file' in mpdcCurrentSong:
            basePath = os.path.join(self._music_directory, os.path.dirname(mpdcCurrentSong['file']))
            path = os.path.join(basePath, 'cover.jpg')
            if not os.path.isfile(path):
                path = os.path.join(basePath, 'cover.png')
                if not os.path.isfile(path):
                    path = os.path.join(basePath, 'cover.gif')
                    if not os.path.isfile(path):
                        path = ''

        if path == self._state:
            return

        (image, draw) = self._prep_image()
        if len(path) > 0:
            cover = Image.open(path)
            image.paste(cover.resize((self._iconWidth, self._iconHeight)))
        else:
            draw.rectangle([self._iconWidth/4, self._iconHeight/4, (3 * self._iconWidth)/4, (3 * self._iconHeight)/4], fill='darkgrey', outline='grey')
            draw.text((self._iconWidth/2, self._iconHeight/2), text='cover', fill='black', anchor='mm', align='center')
        self.set_media(image=image)
        self._state = path

    def apply_new_settings(self, settings):
        self._music_directory = settings['music_directory']

class MpdPlayPause(MpdCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_event_assigner(EventAssigner(
            id = "simple_action_pressed",
            ui_label = "Pressed",
            default_events = [Input.Key.Events.DOWN],
            callback = self.on_key_down,
        ))

    def render_state(self, state) -> None:
        (image, draw) = self._prep_image()
        if state == 'play':
            draw.rectangle([self._iconWidth/5, 0, (self._iconWidth/5)*2, self._iconHeight], fill='white', outline='white')
            draw.rectangle([(self._iconWidth/5) * 3, 0, (self._iconWidth/5)*4, self._iconHeight], fill='white', outline='white')
        else:
            draw.polygon([(0, 0), (self._iconWidth, self._iconHeight/2), (0, self._iconHeight)], fill='white', outline='white')
        self.set_media(image=image)
        self._lastUpdate = time.time()
        self._state = state

    def on_ready(self) -> None:
        (mpdcStatus, _) = self._mpdcon.fetchState()
        state = '???'
        if mpdcStatus is not None and 'state' in mpdcStatus:
            state = mpdcStatus["state"]

        if state == self._state and (time.time() - self._lastUpdate) < 1.0:
            return

        self.render_state(state)

    def on_key_down(self, data) -> None:
        (mpdcStatus, _) = self._mpdcon.fetchState()
        if mpdcStatus is None:
            log.info(f'mpdcStatus is None')
            return
        if 'state' not in mpdcStatus:
            log.info(f'no "state" in mpdcStatus')
            return

        pause = 1 if mpdcStatus["state"] == 'play' else 0
        #log.info(f'pause: {pause}')
        self._mpdcon._mpdc.pause(pause)
        self.render_state('pause' if pause else 'play')
