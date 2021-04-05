# -*- coding:utf-8 -*-
import PySimpleGUI as sg

from minghu6.etc.path import get_home_dir
from minghu6.text.seq_enh import split_whitespace
from minghu6.algs.operator import getone
from minghu6.tools.pwd_keeper import PwdKeeper


def startup_popup(check_username=False):
    startup_popup_layout = [
        [sg.Text('pwd file'), sg.InputText(key='pwd_file'), sg.FileBrowse(initial_folder=get_home_dir())],
        [sg.Checkbox('check username', default=check_username, key='check_username', tooltip='if true, input username'),
         sg.Text('username', ), sg.InputText(key='username')],
        [sg.Text('master password'), sg.Input(password_char='>', key='password')],
        [sg.Open(), sg.Exit()]
    ]

    window = sg.Window('pwd keeper startup').Layout(startup_popup_layout)

    button, values = window.Read()

    return button, values


def main_window_popup(pwd_keeper):
    main_popup_layout = [
        [
            sg.Listbox(values=pwd_keeper.get_labels(), size=(55, 15), change_submits=True,
                       select_mode='LISTBOX_SELECT_MODE_BROWSE', key='listbox'),
            sg.Frame('', [
                [
                    sg.Frame('', [
                        [
                            sg.Frame('', [
                                [sg.ReadButton('Update Label', size=(10, 1), key='update_label'), sg.ReadButton('Add Label', size=(10, 1), key='update_label'),
                                 sg.ReadButton('Del Label', button_color=('white', 'red'), size=(10, 1), key='del_label')],
                                [sg.ReadButton('Update Account', size=(10, 1), key='update_account')]],
                                     border_width=0)
                        ],
                    ], border_width=0)
                ],
                [
                    sg.Frame('', [
                        [sg.Multiline(key='label_content', do_not_clear=True, size=(50, 10))],
                    ])
                ]
            ], border_width=0)
        ]
    ]

    main_window = sg.Window('pwd keeper main window').Layout(main_popup_layout)

    return main_window


def gui():
    check_username = False
    # while True:
    #     # button, values = startup_popup(check_username)
    #     # if button is None or button == 'Exit':
    #     #     exit(69)
    #     #
    #     # path = values['pwd_file']
    #     # pwd = values['password']
    #     # check_username = values['check_username']
    #     # username = values['username']

    path = '/home/minghu6/coding/accounts/pwd_minghu6.txt'
    pwd = ''
    check_username = False
    username = ''

    try:
        pwd_keeper = PwdKeeper(path, pwd, check_username, username)
    except Exception as ex:
        sg.PopupError(repr(ex))
    else:
        while True:
            main_window = main_window_popup(pwd_keeper)
            listbox = main_window.FindElement('listbox')

            label_content_window = main_window.FindElement('label_content')

            while True:
                main_window_button, selected_item = main_window.Read()

                # if main_window_button in ('Add', 'Del', 'Update'):
                #     break

                if not selected_item or not selected_item['listbox']:
                    continue

                if main_window_button == 'update_account' and selected_item['listbox']:
                    label = selected_item['listbox'][0]
                    label_content = multiline_to_label_content(label_content_window.Get())
                    for item in label_content:
                        pwd_keeper.update_account(label, item[0], item[1])

                    continue
                    #label_content_window.Update(label_content)

                try:
                    label = selected_item['listbox'][0]
                    items = pwd_keeper.query_account(label)
                except (KeyError, IndexError) as ex:
                    sg.PopupError(repr(ex))
                    continue
                else:
                    #print(items)
                    pass

                content = label_content_to_multiline(items)
                label_content_window.Update(content)
                # print(multiline_to_label_content(label_content_window.Get()))
                # sg.Popup('{0}, {1}'.format(*item), keep_on_top=True, non_blocking=True)


def label_content_to_multiline(contents):
    result = []
    for each_account in contents:
        result.append('   '.join(each_account))

    return '\n'.join(result)


def multiline_to_label_content(content):
    lines = content.strip().split('\n')

    return [split_whitespace(line) for line in lines]

if __name__ == '__main__':
    gui()
