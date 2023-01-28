import PySimpleGUI as gui
import json

#
# This code is very very ugly, but it works and its not as crucial as the rest of the code
#


def Main(planner: str):
    planner = planner.removesuffix('.json').split('/')[-1]

    template = {"array_names": [], "trace_names": [],
                "sources": [], "blacklisted_types": []}
    group_data = {}
    groups = list(group_data.keys())

    settings = {"auto_group_by_can": False, "auto_group_by_array": False,
                "blacklist_NT": False, "global_blacklist": []}

    def write_json(data):
        with open(f'./resources/{planner}.json', 'w') as f:
            json.dump(data, f, indent=4)

    try:
        with open(f'./resources/{planner}.json', 'r') as f:
            planner_data = json.load(f)
            group_data = planner_data['groupings']
            settings = planner_data['settings']
            groups = list(group_data.keys())
    except FileNotFoundError:
        planner_data = {"settings": settings, "groupings": group_data}
        write_json(planner_data)

    def rename_dict_keys(dict, old_key, new_key):
        dict[new_key] = dict.pop(old_key)

    # Define the window's contents
    layout = [
        [gui.Text("Plot Planner"), gui.Button('Plot Settings',
                                              enable_events=True, key='plot_settings')],
        [gui.Listbox(values=groups, size=(30, 3), key='-LIST-', auto_size_text=True,
                     expand_x=True, expand_y=True, background_color='black', text_color='white')],
        [gui.Button('Edit', enable_events=True, key='-EDIT-'), gui.Button('Add', enable_events=True, key='-ADD-'),
         gui.Button('Delete', enable_events=True, key='-DELETE-'), gui.Button('Rename', enable_events=True, key='-RENAME-')],
    ]

    # Create the window
    gui.change_look_and_feel('DarkGrey12')   # Add a touch of color
    window = gui.Window('Plot Planner', layout=layout,
                        finalize=True, resizable=True, size=(1280, 720))
    try:
        if settings['robot_name'] == '':
            settings['robot_name'] = gui.popup_get_text(
                'Enter Robot Name', 'Robot Name')
        robot_name = settings['robot_name']
        with open(f'./resources/cached/{robot_name}.json', 'r') as f:
            jdata = json.load(f)
            jdata['types'] = ['float', 'int', 'str', 'bool']
    except Exception:
        print('Robot Name Needed for dump info')
        exit(1)

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

    def edit_window(name, group_data):
        # i don't like harcoding things but to make this gui usable ima have too here
        layout = [
            [gui.Text('Entry Names', justification='center', size=(30, 1))],
            [gui.Listbox(values=group_data[name]['trace_names'], size=(30, 5), key='selcted_names', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True),
                gui.Listbox(values=jdata['names'], size=(30, 5), key='possible_names', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True)],
            [gui.Text('Array Names', justification='center', size=(30, 1))],
            [gui.Listbox(values=group_data[name]['array_names'], size=(30, 4), key='selcted_arrays', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True),
                gui.Listbox(values=jdata['arraynames'], size=(30, 4), key='possible_arrays', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True)],
            [gui.Text('Sources', justification='center', size=(30, 1))],
            [gui.Listbox(values=group_data[name]['sources'], size=(30, 2), key='selcted_sources', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True),
                gui.Listbox(values=jdata['sources'], size=(30, 2), key='possible_sources', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True)],
            [gui.Text('Blacklisted Types', justification='center', size=(30, 1))],
            [gui.Listbox(values=group_data[name]['blacklisted_types'], size=(30, 1), key='selcted_types', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True),
                gui.Listbox(values=jdata['types'], size=(30, 1), key='possible_types', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True)],
        ]
        window2 = gui.Window(
            f'Editing {name}', layout=layout, finalize=True, resizable=True, size=(1280, 720))

        def __update_lists():
            window2['selcted_names'].update(
                values=group_data[name]['trace_names'])
            window2['selcted_arrays'].update(
                values=group_data[name]['array_names'])
            window2['selcted_sources'].update(
                values=group_data[name]['sources'])
            window2['selcted_types'].update(
                values=group_data[name]['blacklisted_types'])
        while True:
            __update_lists()
            event, values = window2.read()  # type: ignore
            if event == gui.WIN_CLOSED or event == 'Cancel':
                break
            if event is None:
                break
            # print(event, '<|>', values)
            # let the spaghetti begin
            if values['selcted_names']:
                idx = find(values['selcted_names'][0],
                           group_data[name]['trace_names'])
                group_data[name]['trace_names'].pop(idx)
            if values['selcted_arrays']:
                idx = find(values['selcted_arrays'][0],
                           group_data[name]['array_names'])
                group_data[name]['array_names'].pop(idx)
            if values['selcted_sources']:
                idx = find(values['selcted_sources'][0],
                           group_data[name]['sources'])
                group_data[name]['sources'].pop(idx)
            if values['selcted_types']:
                idx = find(values['selcted_types'][0],
                           group_data[name]['blacklisted_types'])
                group_data[name]['blacklisted_types'].pop(idx)
            if values['possible_names'] and event == 'possible_names':
                if values['possible_names'][0] not in group_data[name]['trace_names']:
                    group_data[name]['trace_names'].append(
                        values['possible_names'][0])
            if values['possible_arrays'] and event == 'possible_arrays':
                if values['possible_arrays'][0] not in group_data[name]['array_names']:
                    group_data[name]['array_names'].append(
                        values['possible_arrays'][0])
            if values['possible_sources'] and event == 'possible_sources':
                if values['possible_sources'][0] not in group_data[name]['sources']:
                    group_data[name]['sources'].append(
                        values['possible_sources'][0])
            if values['possible_types'] and event == 'possible_types':
                if values['possible_types'][0] not in group_data[name]['blacklisted_types']:
                    group_data[name]['blacklisted_types'].append(
                        values['possible_types'][0])
            if event:
                write_json({"settings": settings, "groupings": group_data})
        window2.close()  # type: ignore

    def setting_window(settings):
        layout = [
            [gui.Text('Settings', justification='center', size=(30, 1))],
            [gui.Radio('auto group by can ID', 'can', key='can', default=settings['auto_group_by_can'], enable_events=True),
                gui.Radio('Auto group by array name', 'array', key='array',
                          default=settings['auto_group_by_array'], enable_events=True),
                gui.Radio('Blacklist NT', 'nt', key='nt', default=settings['blacklist_NT'], enable_events=True)],
            [gui.Text('Global Blacklist', justification='center', size=(30, 1))],
            [gui.Listbox(values=settings['global_blacklist'], size=(30, 5), key='global_blacklist', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True),
                gui.Listbox(values=jdata['names'], size=(30, 5), key='possible_names', auto_size_text=True, expand_x=True, expand_y=True, enable_events=True)],
            [gui.Text('Robot Name', justification='left', size=(30, 1)), gui.Input(
                key='robot_name', size=(30, 1), enable_events=True)],
        ]
        window3 = gui.Window('Settings', layout=layout,
                             finalize=True, resizable=True, size=(1280, 720))

        def __update_lists():
            window3['global_blacklist'].update(
                values=settings['global_blacklist'])
        while True:
            __update_lists()
            for i in window3.element_list():
                print(f'{i} -> {i.key}')
            event, values = window3.read()  # type: ignore
            if event == gui.WIN_CLOSED or event == 'Cancel':
                break
            if event is None:
                break
            # print(event, '<|>', values)
            if values['global_blacklist']:
                idx = find(values['global_blacklist'][0],
                           settings['global_blacklist'])
                settings['global_blacklist'].pop(idx)
            if values['possible_names'] and event == 'possible_names':
                if values['possible_names'][0] not in settings['global_blacklist']:
                    settings['global_blacklist'].append(
                        values['possible_names'][0])
            if event == 'can':
                settings['auto_group_by_can'] = not settings['auto_group_by_can']
                window3.element_list()[1].update(
                    value=settings['auto_group_by_can'])
            if event == 'array':
                settings['auto_group_by_array'] = not settings['auto_group_by_array']
                window3.element_list()[2].update(
                    value=settings['auto_group_by_array'])
            if event == 'nt':
                settings['blacklist_NT'] = not settings['blacklist_NT']
                window3.element_list()[3].update(
                    value=settings['blacklist_NT'])
            if values['robot_name'] and event == 'robot_name':
                settings['robot_name'] = values['robot_name']
            if event:
                write_json({"settings": settings, "groupings": group_data})
        window3.close()

    # Display and interact with the Window using an Event Loop
    while True:
        update_list()
        event, values = window.read()  # type: ignore
        # See if user wants to quit or window was closed
        if event == gui.WIN_CLOSED or event == 'Cancel':
            break
        if event is None:
            break
        if event == '-DELETE-':
            del group_data[values['-LIST-'][0]]
        if event == '-ADD-':
            group_data[gui.popup_get_text(
                'Rename Group', 'Enter new name', default_text='New Group')] = template.copy()
        if event == '-RENAME-':
            new = gui.popup_get_text(
                'Rename Group', 'Enter new name', default_text=values['-LIST-'][0])
            rename_dict_keys(group_data, values['-LIST-'][0], new)
        if event == '-EDIT-':
            edit_window(values['-LIST-'][0], group_data)
        if event == 'plot_settings':
            setting_window(settings)
        if event:
            write_json({"settings": settings, "groupings": group_data})
