# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow

# Import python modules
import os

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class SimpleAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_label_switch = SwitchRow(
            action_core=self,
            var_name="show_label",
            default_value=False,
            title="Show label",
            on_change=self.on_show_label_changed
        )
        
    def on_ready(self) -> None:
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        self.set_media(media_path=icon_path, size=1.00)
        if self.get_settings().get("show_label", False):
            self.set_bottom_label("hello")
        else:
            self.set_bottom_label("")

    def get_config_rows(self):
        return self.get_generative_ui_widgets()
        
    def on_show_label_changed(self, widget, new_value, old_value):
        self.on_ready()  # redraw with the new setting

    def on_key_down(self) -> None:
        print("Key down")
    
    def on_key_up(self) -> None:
        print("Key up")
