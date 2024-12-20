
from pathlib import Path
import configparser


__all__ = ["Controller"]
WINDOW_CLOSED = None


class Controller:
    def __init__(self, settings_filename=None):
        """ Create Controller instance """
        self.view = None
        self.model = None
        self.settings = None
        self.settings_filename = settings_filename

        # FreeSimpleGUI variables
        self.window = None
        self.event = None
        self.values = None

        # Loading other settings from config file
        if settings_filename:
            self.settings = self.load_settings_from_file(settings_filename)
        # Or use defaults
        if not self.settings or not settings_filename:
            self.settings = self.load_default_settings()
        return

    @staticmethod
    def load_settings_from_file(settings_filename):
        """Load settings from config file."""

        if not Path(settings_filename).is_file():  # if filename is no complete path or file does not exist
            # try to look in cwd for filename
            settings_filename = Path(str(Path.cwd()), settings_filename)
            if not Path(settings_filename).is_file():
                return None

        # create the settings object
        settings = configparser.ConfigParser(allow_no_value=True)
        settings.read(settings_filename)
        return settings

    @staticmethod
    def load_default_settings():
        defaults = {"GUI": {"font_size": "14",
                            "font_family": "Arial",
                            "theme": "SandyBeach",
                            "last_file": ""}, }
        settings = configparser.ConfigParser()
        settings.read_dict(defaults)
        return settings

    def set_view(self, view):
        """This function prepares the GUI in a useful state for first usage"""
        self.view = view

        if self.settings:
            self.view.update_gui_settings()
            self.view.settings_filename = self.settings_filename

        self.view.move_up_left(self.view.main_window)
        return

    def mainloop(self):
        """Controller mainloop"""
        while True:
            self.event, self.values = self.view.main_window.read()
            if self.event in (WINDOW_CLOSED, "Beenden"):
                break
            if self.event == "Über":
                self.view.about_window()
            if self.event == "Einstellungen":
                settings_to_save = self.view.settings_window()
                if settings_to_save:
                    self.view.update_gui_settings()
                    try:
                        with open(self.settings_filename, 'w') as configfile:
                            self.settings.write(configfile)
                    except Exception as e:
                        text = f"User settings could not be saved to file:\n" \
                               f"'{self.settings_filename}'\n{e}"
                        self.view.popup(title='User Settings save error',
                                        text=text)
                    else:
                        # Display success message
                        self.view.popup(title="", text="Einstellungen gespeichert!")
                    self.view.main_window.close()
                    self.view.make_main_window()
                    self.view.move_up_left(self.view.main_window)
            if self.event == "-IN-":
                if not Path(self.values['-IN-']).is_file():
                    self.view.main_window['-IN-'].update('')
            if self.event == "-START_BUTTON-":
                self.start_button_pressed()

        self.view.main_window.close()  # Close GUI, return to main()
        return

    def start_button_pressed(self):
        """ Here the analysis and file generation is controlled. """

        # Check, if given filepath is valid
        if not Path(self.values['-IN-']).is_file():
            self.view.main_window['-IN-'].update('')
            return
        path = self.values['-IN-']
        new_file_content = open(path, "rb").read() + b'\x00'
        new_file_name = path[:-5] + "_EDIT_.xlsx"

        # Check if file is in use
        if self.is_file_in_use(new_file_name):
            title = 'Datei bereits geöffnet'
            question_text = f"Eine gleichnamige Datei\n'{new_file_name}'\n" \
                            f"ist bereits in einer anderen Anwendung geöffnet.\n" \
                            "\nBitte schließen Sie diese Anwendung."
            self.view.popup(title=title, text=question_text)
            return

        new_file = open(new_file_name, "wb")
        new_file.write(new_file_content)
        new_file.close()
        self.view.popup(text=f"Neue Datei wurde erzeugt:\n{new_file_name}", title="Datei repariert")
        return

    @staticmethod
    def is_file_in_use(filename):
        if Path(filename).is_file():
            try:
                Path(filename).rename(filename)
            except OSError as error_message:
                # Controller.logger.error(f"Zugriffs-Fehler auf Datei '{filename}'! {error_message}")
                return True
        # Controller.logger.debug(f"File '{filename}' can be accessed in write-mode.")
        return False

    def set_model(self, model):
        """Setting model for controller"""
        self.model = model


def module_testing():
    """Module testing"""
    print(f"Testing module '{__file__}'")
    controller = Controller("config.ini")

    for var in vars(controller):
        print(f"{var:_<40}{repr(vars(controller)[var])}")


if __name__ == '__main__':
    module_testing()
