import datetime

import PySimpleGUI as sg


def main():
    """ main event loop """

    layout = [
        [
            sg.Multiline(
                key="diary", size=(85, 25), autoscroll=True, font=("Times", 12, "")
            )
        ],
        [sg.StatusBar("Status information will be here")],
        [sg.Button("Datestamp"), sg.Button("Horizontal line"), sg.Button("Save")],
    ]

    window = sg.Window(
        "Diary", layout, grab_anywhere=True,
    )

    diary = window["diary"]

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            break
        elif event == "Datestamp":
            now = datetime.datetime.now()
            stamp = f"\n{'=' * 6} [ {now.strftime('%Y-%m-%d %H:%M:%S')} ] {'=' * 6}\n"
            diary.update(value=stamp, append=True)
        elif event == "Horizontal line":
            diary.update(value="\n" + "_" * 80 + "\n", append=True)

    window.close()


if __name__ == "__main__":
    main()
