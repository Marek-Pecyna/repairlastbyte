""" make a complete standalone app with:
    "pyinstaller .\\main.spec"
"""


from Controller import Controller
from Constants import APP_TITLE, VERSION, SETTINGS_FILENAME
from View import View

__author__ = "Dr. Marek Pecyna, https://daten-entdecker.de/"


def main():
    controller = Controller(SETTINGS_FILENAME)
    view = View(title=f"{APP_TITLE} {VERSION}", settings=controller.settings)
    controller.set_view(view)
    controller.mainloop()


if __name__ == '__main__':
    main()

