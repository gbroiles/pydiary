import datetime
import pynacl
import dropbox
import PySimpleGUI as sg

def main():
    """ main event loop """

    layout1 = [
            sg.Multiline(key="diary", size=(85, 40), autoscroll=False),
    ]


    layout = [

        [sg.Button("Datestamp"), sg.Button("Save")],
    ]

    window = sg.Window(
        "Diary",
        layout,
        return_keyboard_events=True,
        grab_anywhere=False,
                size=(650, 200),
    )




if __name__ == "__main__":
    main()

