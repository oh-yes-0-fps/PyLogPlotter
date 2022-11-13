import PySimpleGUI as gui

template = {
            "array_names": [],
            "trace_names": [],
            "sources": [],
            "blacklisted_types": []
        }

group_data = {}

groups = list(group_data.keys())



def rename_dict_keys(dict, old_key, new_key):
    dict[new_key] = dict.pop(old_key)



# Define the window's contents
layout = [
            [gui.Text("Plot Planner"), gui.Button('Plot Settings', enable_events=True, key='plot_settings')],
            [gui.Listbox(values=groups, size=(30, 3), key='-LIST-', auto_size_text=True)],
            [gui.Button('Edit', enable_events=True, key='-EDIT-'), gui.Button('Add', enable_events=True, key='-ADD-'), gui.Button('Delete', enable_events=True, key='-DELETE-'), gui.Button('Rename', enable_events=True, key='-RENAME-')],
         ]

# Create the window
gui.change_look_and_feel('DarkGrey12')   # Add a touch of color
window = gui.Window('Plot Planner', layout=layout, finalize=True, resizable=True)
window['-LIST-'].expand(expand_x=True, expand_y=True)


def find(str, list):
    for i in range(len(list)):
        if str == list[i]:
            return i
    return 0

def update_list():
    # new_groups = []
    # for i in group_data:
    #     new_groups.append(i)
    # groups = new_groups
    groups = list(group_data.keys())
    window['-LIST-'].update(values=groups)

# Display and interact with the Window using an Event Loop
while True:
    update_list()
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == gui.WIN_CLOSED or event == 'Cancel':
        break
    if event is None:
        break
    if event == '-DELETE-':
        del group_data[values['-LIST-'][0]]
    if event == '-ADD-':
        group_data[gui.popup_get_text('Rename Group', 'Enter new name', default_text='New Group')] = template.copy()
    if event == '-RENAME-':
        new = gui.popup_get_text('Rename Group', 'Enter new name', default_text=values['-LIST-'][0])
        rename_dict_keys(group_data, values['-LIST-'][0], new)
    # if event == '-EDIT-':

