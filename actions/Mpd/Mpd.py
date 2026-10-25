# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.ActionCore import ActionCore
#from src.backend.DeckManagement.DeckController import DeckController
#from src.backend.PageManagement.Page import Page
#from src.backend.PluginManager.PluginBase import PluginBase
#from GtkHelper.GenerativeUI.SwitchRow import SwitchRow

# Import python modules
import os

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from PIL import Image, ImageDraw
from mpd import MPDClient

class MpdProgress(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.show_label_switch = SwitchRow(
        #    action_core=self,
        #    var_name="show_label",
        #    default_value=False,
        #    title="Show label",
        #    on_change=self.on_show_label_changed
        #)
        self.mpdc = None
        image_format = self.deck_controller.deck.key_image_format()
        (self.image_width, self.image_height) = image_format['size']
        
    def on_ready(self) -> None:
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        self.set_media(media_path=icon_path, size=0.50)
        #if self.get_settings().get("show_label", False):
        #    self.set_bottom_label("hello")
        #else:
        #    self.set_bottom_label("")
        if self.mpdc is None:
            self.mpdc = MPDClient()
            try:
                # Add try-catch to handle lack of MPD
                #mpdc.connect(args[0], args[1])
                self.mpdc.connect("localhost", 6600)
            except Exception as err:
                print(f'Unexpected {err=}, {type(err)=}')
                self.mpdc = None
                return

        try:
            mpdcStatus = self.mpdc.status()
            #print(f'mpdcStatus: {mpdcStatus}')
            mpdcCurrentSong = self.mpdc.currentsong()
            #print(f'mpdcCurrentSong: {mpdcCurrentSong}')
        except Exception as err:
            print(f'Unexpected {err=}, {type(err)=}')
            self.mpdc = None
            return

        if set(['elapsed', 'duration', 'song', 'playlistlength']).issubset(mpdcStatus):
            elapsedMinutes = int(float(mpdcStatus["elapsed"]) / 60)
            elapsedSeconds = int(float(mpdcStatus["elapsed"]) % 60)
            durationMinutes = int(float(mpdcStatus["duration"]) / 60)
            durationSeconds = int(float(mpdcStatus["duration"]) % 60)
            percent = int((float(mpdcStatus["elapsed"]) * 100) / float(mpdcStatus["duration"]))
            songIndex = int(mpdcStatus['song']) + 1
            playlistLength = int(mpdcStatus['playlistlength'])
            #state = '{}={}:{:>02}\n{}:{:>02}\n{}%\n{} / {}'.format(mode, elapsedMinutes, elapsedSeconds, durationMinutes, durationSeconds, percent, songIndex, playlistLength)
            state = '{}:{:>02}\n{}:{:>02}\n{}%\n{} / {}'.format(elapsedMinutes, elapsedSeconds, durationMinutes, durationSeconds, percent, songIndex, playlistLength)
        else:
            #state = f'{mode}={mpdcStatus["state"]}'
            state = f'{mpdcStatus["state"]}'

        #draw = ImageDraw.Draw(inputImage)
        #width = inputImage.size[0]
        #height = inputImage.size[1]
        #draw.rectangle([0, 0, width, height], fill="black", outline="black")
        image = Image.new("RGB", (self.image_width, self.image_height), "black")
        draw = ImageDraw.Draw(image)


        draw.text((self.image_width/2, self.image_height/2), text=state, fill='white', anchor='mm', align='center')
        self.set_media(image=image)

    #def get_config_rows(self):
    #    return self.get_generative_ui_widgets()
        
    #def on_show_label_changed(self, widget, new_value, old_value):
    #    self.on_ready()  # redraw with the new setting

    #def on_key_down(self) -> None:
    #    print("Key down")
    #
    #def on_key_up(self) -> None:
    #    print("Key up")




# import os
# import time
# 
# from PIL import Image, ImageDraw
# from mpd import MPDClient
# from streamdeck_ui.config import DEFAULT_FONT
# 
# mpdc = None
# previousRunTime = 0.0
# previousState = 'unknown'
# 
# def detectState(args: list[str]) -> str:
#     global mpdc
#     global previousRunTime
#     global previousState
#     state = 'unknown'
# 
#     if mpdc is None:
#         mpdc = MPDClient()
#         try:
#             # Add try-catch to handle lack of MPD
#             mpdc.connect(args[0], args[1])
#         except Exception as err:
#             print(f'Unexpected {err=}, {type(err)=}')
#             mpdc = None
#             return previousState
# 
#     # prevent re-calculation too quick
#     if (time.time() - previousRunTime) < 0.9:
#         return previousState
#     previousRunTime = time.time()
# 
#     try:
#         mpdcStatus = mpdc.status()
#         #print(f'mpdcStatus: {mpdcStatus}')
#         mpdcCurrentSong = mpdc.currentsong()
#         #print(f'mpdcCurrentSong: {mpdcCurrentSong}')
#     except Exception as err:
#         print(f'Unexpected {err=}, {type(err)=}')
#         mpdc = None
#         return previousState
# 
#     #if not set(['state', 'elapsed', 'duration']).issubset(mpdcStatus):
#     if not set(['state']).issubset(mpdcStatus):
#         print(f'Invalid mpdcStatus {mpdcStatus}')
#         mpdc = None
#         return previousState
#     #if not set(['artist', 'album', 'track', 'title']).issubset(mpdcCurrentSong):
#     #    print(f'Invalid mpdcCurrentSong {mpdcCurrentSong}')
#     #    mpdc = None
#     #    return previousState
# 
#     #previousRunTime = time.time()
# 
#     mode = args[2]
#     state = f'{mode}={mode}'
#     if mode == 'state':
#         state = f'{mode}={mpdcStatus["state"]}'
#     elif mode == 'artist':
#         if 'artist' in mpdcCurrentSong:
#             state = f'{mode}={mpdcCurrentSong["artist"]}'
#     elif mode == 'album':
#         if 'album' in mpdcCurrentSong:
#             state = f'{mode}={mpdcCurrentSong["album"]}'
#     elif mode == 'artist_album':
#         if set(['artist', 'album']).issubset(mpdcCurrentSong):
#             state = f'{mode}={mpdcCurrentSong["artist"]}\n\n{mpdcCurrentSong["album"]}'
#     elif mode == 'song':
#         if set(['track', 'title']).issubset(mpdcCurrentSong):
#             state = f'{mode}={mpdcCurrentSong["track"]} - {mpdcCurrentSong["title"]}'
#     elif mode == 'progress':
#         if set(['elapsed', 'duration', 'song', 'playlistlength']).issubset(mpdcStatus):
#             elapsedMinutes = int(float(mpdcStatus["elapsed"]) / 60)
#             elapsedSeconds = int(float(mpdcStatus["elapsed"]) % 60)
#             durationMinutes = int(float(mpdcStatus["duration"]) / 60)
#             durationSeconds = int(float(mpdcStatus["duration"]) % 60)
#             percent = int((float(mpdcStatus["elapsed"]) * 100) / float(mpdcStatus["duration"]))
#             songIndex = int(mpdcStatus['song']) + 1
#             playlistLength = int(mpdcStatus['playlistlength'])
#             state = '{}={}:{:>02}\n{}:{:>02}\n{}%\n{} / {}'.format(mode, elapsedMinutes, elapsedSeconds, durationMinutes, durationSeconds, percent, songIndex, playlistLength)
#         else:
#             state = f'{mode}={mpdcStatus["state"]}'
#     elif mode == 'cover':
#         if 'file' in mpdcCurrentSong:
#             basePath = os.path.join('/home/kda/hdmusic/', os.path.dirname(mpdcCurrentSong['file']))
#             path = os.path.join(basePath, 'cover.jpg')
#             if not os.path.isfile(path):
#                 path = os.path.join(basePath, 'cover.png')
#                 if not os.path.isfile(path):
#                     path = os.path.join(basePath, 'cover.gif')
#                     if not os.path.isfile(path):
#                         path = ''
#             state = f'{mode}={path}'
#         else:
#             state = f'{mode}='
# 
#     print(f'detectState: state={state}')
#     previousState = state
#     return state
# 
# def prepareImage(inputImage: Image, state: str) -> Image:
#     if state is None:
#         return inputImage
#     index = state.find('=')
#     if index < 1:
#         return inputImage
#     mode = (state[:index]).strip()
#     value = (state[index+1:]).strip()
# 
#     draw = ImageDraw.Draw(inputImage)
#     width = inputImage.size[0]
#     height = inputImage.size[1]
#     draw.rectangle([0, 0, width, height], fill="black", outline="black")
#     if mode == 'state':
#         if value == 'play':
#             draw.rectangle([width/5, 0, (width/5)*2, height], fill='white', outline='white')
#             draw.rectangle([(width/5) * 3, 0, (width/5)*4, height], fill='white', outline='white')
#         else:
#             draw.polygon([(0, 0), (inputImage.size[0], inputImage.size[1]/2), (0, inputImage.size[1])], fill='white', outline='white')
#     elif mode == 'artist' or mode == 'album' or mode == 'song' or mode == 'artist_album':
#         allLines = []
#         for valueLine in value.splitlines():
#             textWidth = draw.textlength(valueLine)
#             lines = []
#             if textWidth > width:
#                 valuePieces = valueLine.split(' ')
#                 valuePieceIndex = 0
#                 while valuePieceIndex < len(valuePieces):
#                     line = valuePieces[valuePieceIndex]
#                     valuePieceIndex += 1
#                     textWidth = draw.textlength(line)
#                     if textWidth > width:
#                         lines.append(line)
#                         continue
#                     while textWidth < width:
#                         if valuePieceIndex >= len(valuePieces):
#                             lines.append(line)
#                             line = ''
#                             break
#                         if len(line) > 0:
#                             line += ' '
#                         line += valuePieces[valuePieceIndex]
#                         valuePieceIndex += 1
#                         textWidth = draw.textlength(line)
#                     if len(line) > 0:
#                         line = line[:line.rfind(' ')]
#                         valuePieceIndex -= 1
#                         lines.append(line)
#                 normalizedValue = '\n'.join(lines)
#             else:
#                 normalizedValue = valueLine
#             allLines.append(normalizedValue)
#         allLinesMerged = '\n'.join(allLines)
#         #print(f'allLinesMerged: {allLinesMerged}')
#         draw.text((width/2, height/2), text=allLinesMerged, fill='white', anchor='mm', align='center')
#     elif mode == 'progress':
#         draw.text((width/2, height/2), text=value, fill='white', anchor='mm', align='center')
#     elif mode == 'cover':
#         if len(value) > 0:
#             cover = Image.open(value)
#             inputImage.paste(cover.resize((width, height)))
#         else:
#             draw.rectangle([width/4, height/4, (3 * width)/4, (3 * height)/4], fill='darkgrey', outline='grey')
#             draw.text((width/2, height/2), text='cover', fill='black', anchor='mm', align='center')
# 
#     return inputImage
