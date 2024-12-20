import FreeSimpleGUI as sg

from Constants import DEFAULT_FILE
import webbrowser

__all__ = ['View']


class View:
    """ Class for Main-GUI """
    # logger = logging.getLogger().getChild(__name__)
    def __init__(self, title="", settings=None):
        self.title = title
        self.settings_filename = ""
        self.settings = settings
        self.update_gui_settings()
        self.main_window = None
        self.make_main_window()
        return

    def make_main_window(self):
        """ Define and creates main application window with PySimpleGUI """

        # ------ Menu Definition ------ #
        menu_def = [
            ["&Datei", ["&Beenden"]],
            ["&Hilfe", ["&Über", "&Einstellungen"]]
        ]

        # ------ GUI Definition ------ #
        file_types = (("Alle Dateien", "*.*"),)
        font = "Arial"
        font_size = 11
        font_size_title = int(font_size * 1.4)
        default_text = DEFAULT_FILE

        if self.settings:
            font = self.settings["GUI"]["font_family"]
            font_size = int(self.settings["GUI"]["font_size"])
            font_size_title = int(font_size * 1.4)

        header = sg.Text("", font=(font, font_size_title),
                         expand_x=True, justification="c")

        source_file_layout = [
            [sg.Input(key="-IN-", s=40, enable_events=True,
                      readonly=True, expand_x=True,
                      default_text=default_text),
             sg.FileBrowse(button_text="Datei", s=14,
                           file_types=file_types)],
        ]

        source_file_frame = sg.Frame("Datei auswählen", source_file_layout, pad=(0, 10),
                                     key='-SOURCE_FRAME-', expand_x=True)

        compute_frame = sg.Frame("Optionale Parameter", [], pad=(0, 10), expand_x=True)

        layout = [
            [sg.MenuBar(menu_def, tearoff=False)],
            [header],
            [source_file_frame],
            [compute_frame],
            [sg.B("Datei reparieren", button_color="tomato", s=16, key='-START_BUTTON-',
                  bind_return_key=True, expand_x=True)],
            [sg.VPush()],
            [sg.Sizegrip()]
        ]
        self.main_window = sg.Window(title=self.title,
                                     layout=layout,
                                     finalize=True,
                                     grab_anywhere=True,
                                     resizable=True)
        self.main_window.set_min_size(self.main_window.size)
        return

    def make_settings_window(self, settings_filename="", size=(450, 400)):
        """
        Define and creates settings window with FreeSimpleGUI.
        Reads all settings from dict 'self.setting'.
        Default parameter 'settings_filename' is used for window title.
        """

        if self.settings:
            layout = []
            text_size = 10
            combo_size = 20
            input_size = 40
            current_theme = sg.theme()
            for section in self.settings.sections():
                layout.append([sg.Text(section)])
                for item in self.settings[section]:
                    if item == "theme":
                        layout.append([
                            sg.Text(item, s=text_size, justification="l"),
                            sg.Combo(values=sg.theme_list(), s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_theme,
                                     readonly=True,
                                     enable_events=True)], )
                    elif item == "font_size":
                        fonts = list(range(8, 19))
                        current_font_size = self.settings["GUI"]["font_size"]
                        layout.append([
                            sg.Text(item, s=text_size, justification="l"),
                            sg.Combo(values=fonts, s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_font_size,
                                     readonly=True,
                                     enable_events=True)])
                    elif item == "font_family":
                        fonts = sg.Text.fonts_installed_list()
                        current_font_family = self.settings["GUI"]["font_family"]
                        layout.append([
                            sg.Text(item, s=text_size, justification="l"),
                            sg.Combo(values=fonts, s=combo_size, key=f"-{item.upper()}-",
                                     default_value=current_font_family,
                                     readonly=True,
                                     enable_events=True)])
                    else:
                        if len(self.settings[section][item]) > input_size:
                            layout.append([
                                sg.Text(item, s=text_size, justification="l"),
                                sg.Multiline(self.settings[section][item], s=(input_size, 2), enable_events=True,
                                             expand_x=True, expand_y=True, justification='left',
                                             key=f"-{item.upper()}-")
                            ])
                        else:
                            layout.append([
                                sg.Text(item, s=text_size, justification="l"),
                                sg.Input(self.settings[section][item], s=input_size,
                                         key=f"-{item.upper()}-")
                            ])
                layout.append([sg.HSeparator()])

            scroll_column = sg.Column(layout=layout, scrollable=True, vertical_scroll_only=True,
                                      expand_x=True, expand_y=True, size=size, pad=(0, 0))
            win_layout = [
                [scroll_column],
                [sg.Push(), sg.Button("Speichern", s=20, bind_return_key=True), sg.Push(), sg.Sizegrip()]
            ]
            return sg.Window(f'Einstellungen "{settings_filename}"',
                             layout=win_layout, finalize=True, grab_anywhere=True,
                             use_custom_titlebar=True, modal=True, resizable=True)

    def settings_window(self) -> bool:
        """
        Shows setting window and manage user interactions
        :return True, if settings should be saved. False, if not:
        """

        window = self.make_settings_window(self.settings_filename)
        window.set_min_size(window.size)
        View.move_up(window)
        current_theme = self.settings['GUI']['THEME']
        current_font = self.settings['GUI']['FONT_FAMILY']
        current_font_size = self.settings['GUI']['FONT_SIZE']
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                return False
            if event == "Speichern":
                for section in self.settings.sections():
                    for item in self.settings[section]:
                        self.settings[section][item] = str(values[f"-{item.upper()}-"])
                window.close()
                return True
            # if the theme was changed, restart the window
            if event in ['-THEME-', '-FONT_SIZE-', '-FONT_FAMILY-']:
                self.settings['GUI']['THEME'] = str(values['-THEME-'])
                self.settings['GUI']['FONT_FAMILY'] = str(values['-FONT_FAMILY-'])
                self.settings['GUI']['FONT_SIZE'] = str(values['-FONT_SIZE-'])
                self.update_gui_settings()
                window.close()
                window = self.make_settings_window(self.settings_filename)
                window.set_min_size(window.size)
                View.move_up(window)
                self.settings['GUI']['THEME'] = current_theme
                self.settings['GUI']['FONT_FAMILY'] = current_font
                self.settings['GUI']['FONT_SIZE'] = current_font_size
                self.update_gui_settings()

    def about_window(self):
        """ Show a small modal 'About' window with contact information """

        window_title = "Über..."
        text = ["Dieses Tool hängt ein Null-Byte am Dateiende an.",
                "",
                ]
        layout = [[sg.T(self.title, font=("Arial", 15), text_color="red")]]

        for line in text:
            layout.append([sg.T(line)])
        layout.append([sg.T("Entwickelt von Datenanalyse Dr. Pecyna", font=("Arial", 15))])
        layout.append([sg.B("E-Mail", use_ttk_buttons=True,
                       expand_x=True,
                       key="-EMAIL-")])
        layout.append([sg.B("https://daten-entdecker.de", use_ttk_buttons=True,
                       expand_x=True,
                       key="-WEBSITE-")])
        choice, _ = sg.Window(window_title, layout=layout,
                              use_custom_titlebar=True,
                              modal=True,
                              grab_anywhere=True).read(close=True)
        if choice == "-WEBSITE-":
            webbrowser.open_new_tab(r'https://daten-entdecker.de')
        if choice == "-EMAIL-":
            webbrowser.open_new_tab(f"mailto:info@daten-entdecker.de?subject='Contact {self.title}'")
        return

    @staticmethod
    def move_up(window):
        screen_width, screen_height = window.get_screen_dimensions()
        win_width, win_height = window.size
        x, y = (screen_width - win_width) // 2, 0
        window.move(x, y)

    @staticmethod
    def move_up_left(window):
        window.move(0, 0)

    def update_gui_settings(self):
        """ Update GUI settings from dict 'self.settings' passed during __init__ """
        if self.settings:
            theme = self.settings["GUI"]["theme"]
            font_family = self.settings["GUI"]["font_family"]
            font_size = int(self.settings["GUI"]["font_size"])
            font_style = "normal"  # italic roman bold normal underline overstrike
            sg.theme(theme)
            sg.set_options(font=(font_family, font_size, font_style))
        return

    @staticmethod
    def not_implemented():
        sg.popup_error("Funktion noch nicht implementiert.")
        return

    @staticmethod
    def popup(title, text):
        sg.popup(text, title=title)
        return


def module_test():
    """Module testing"""
    import configparser

    print("Module Testing")
    settings_dict = {"GUI": {"font_size": "14",
                             "font_family": "Arial",
                             "theme": "DarkTeal10",
                             'last_file': ""},
                     }

    settings = configparser.ConfigParser()
    settings.read_dict(settings_dict)

    v = View("View Module Testing", settings)
    while True:
        event, values = v.main_window.read()
        if event in (sg.WINDOW_CLOSED, "Beenden"):
            break
        if event == "Einstellungen":
            v.make_settings_window('Config.ini')
        if event == "Über":
            v.about_window()
    return


if __name__ == '__main__':
    module_test()
