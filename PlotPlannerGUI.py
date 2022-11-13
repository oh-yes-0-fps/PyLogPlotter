import PySimpleGUI as gui

# Define the window's contents
layout = [
            [gui.Text("Plot Planner")],
            [gui.Listbox(values=('Plot 1', 'Plot 2', 'Plot 3'), size=(30, 3), key='-LIST-')],
            [gui.Button('Edit', enable_events=True, key='-EDIT-'), gui.Button('Add', enable_events=True, key='-ADD-'), gui.Button('Delete', enable_events=True, key='-DELETE-')]
         ]

# Create the window
gui.change_look_and_feel('DarkGrey12')   # Add a touch of color
window = gui.Window('Plot Planner', layout=layout, finalize=True, resizable=True)
window['-LIST-'].expand(expand_x=True, expand_y=True)


# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == gui.WIN_CLOSED or event == 'Cancel':
        break
    try:
        print('You selected ', values['-LIST-'][0])
    except:
        pass
