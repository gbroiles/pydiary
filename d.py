import datetime
import nacl
import dropbox
import PySimpleGUI as sg
import pprint


def main():
    """ main event loop """

    layout = [
        [
            sg.Multiline(
                key="diary", size=(85, 25), autoscroll=True, font=("Times", 12, "")
            )
        ],
        [sg.Button("Datestamp"), sg.Button("Horizontal line"), sg.Button("Save")],
    ]

    window = sg.Window(
        "Diary", layout, return_keyboard_events=True, grab_anywhere=False,
    )

    diary = window.FindElement("diary")

    while True:
        event, values = window.read()
        if event in (None, "Cancel"):
            break
        if event == "Datestamp":
            now = datetime.datetime.now()
            spacer = "=" * 6
            stamp = (
                "\n" + spacer + " [ " + now.strftime("%X %x") + " ] " + spacer + "\n"
            )
            diary.update(value=stamp, append=True)
        if event == "Horizontal line":
            diary.update(value=("\n" + "-" * 30 + "\n"), append=True)

    window.close()


if __name__ == "__main__":
    main()
