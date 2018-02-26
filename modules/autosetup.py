import os, sys

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

from modules import get_banner

nebula_dir = sys.path[0]

def autosetup(lib, install_dir, game_name):

    parser = ConfigParser()

    if lib == 'goglib':
        banners_dir = os.getenv('HOME') + '/.games_nebula/images/goglib/'
        path_0 = os.getenv('HOME') + '/.games_nebula/scripts/goglib/autosetup.ini'
        path_1 = nebula_dir + '/scripts/goglib/autosetup.ini'
    elif lib == 'mylib':
        banners_dir = os.getenv('HOME') + '/.games_nebula/images/mylib/'
        path_0 = os.getenv('HOME') + '/.games_nebula/scripts/mylib/autosetup.ini'
        path_1 = nebula_dir + '/scripts/mylib/autosetup.ini'

    if os.path.exists(path_0):
        parser.read(path_0)
    else:
        parser.read(path_1)

    if parser.has_section(game_name):

        if parser.has_option(game_name, 'image'):
            image = parser.get(game_name, 'image')
            if image != '':
                print("Downloading image")
                get_banner.get_banner(game_name, image, banners_dir, lib)

        if parser.has_option(game_name, 'native_exe'):
            native_exe = parser.get(game_name, 'native_exe')
            if native_exe != '':
                print("Writing start.sh")

                start_file_path = install_dir + '/' + game_name + '/start.sh'
                start_gog_path = install_dir + '/' + game_name + '/start_gog.sh'

                if os.path.exists(start_file_path):
                    os.system('mv ' + start_file_path + ' ' + start_gog_path)

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_native.py" ' + game_name]

                start_file = open(start_file_path, 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + start_file_path)

                if '/' in native_exe:
                    native_exe_dir = native_exe.split('/')[0]
                    native_exe = native_exe.split('/')[1]
                    start_gn_lines = ['#!/bin/bash\n',
                    'cd "$INSTALL_DIR/' + game_name + '/game/' + native_exe_dir + '"\n',
                    './' + native_exe]
                else:
                    start_gn_lines = ['#!/bin/bash\n',
                    'cd "$INSTALL_DIR/' + game_name + '/game"\n',
                    './' + native_exe]

                start_gn_file_path = install_dir + '/' + game_name + '/start_gn.sh'
                start_gn_file = open(start_gn_file_path, 'w')
                for line in start_gn_lines:
                    start_gn_file.write(line)
                start_gn_file.close()
                os.system('chmod +x ' + start_gn_file_path)

        if parser.has_option(game_name, 'native_settings_exe'):
            native_settings_exe = parser.get(game_name, 'native_settings_exe')
            if native_settings_exe != '':
                print("Writing settings.sh")

                if '/' in native_settings_exe:
                    native_settings_exe_dir = native_settings_exe.split('/')[0]
                    native_settings_exe = native_settings_exe.split('/')[1]
                    start_gn_lines = ['#!/bin/bash\n',
                    'cd "$INSTALL_DIR/' + game_name + '/game/' + native_settings_exe_dir + '"\n',
                    './' + native_settings_exe]
                else:
                    start_gn_lines = ['#!/bin/bash\n',
                    'cd "$INSTALL_DIR/' + game_name + '/game"\n',
                    './' + native_settings_exe]

                start_gn_file_path = install_dir + '/' + game_name + '/settings.sh'
                start_gn_file = open(start_gn_file_path, 'w')
                for line in start_gn_lines:
                    start_gn_file.write(line)
                start_gn_file.close()
                os.system('chmod +x ' + start_gn_file_path)

        if parser.has_option(game_name, 'win_exe'):
            win_exe = parser.get(game_name, 'win_exe')
            if win_exe != '':
                print("Writing start.sh")

                if parser.has_option(game_name, 'winedlloverrides'):
                    overrides = parser.get(game_name, 'winedlloverrides')
                    start_lines = ['#!/bin/bash\n',
                    'export WINEDLLOVERRIDES="' + overrides + '"\n',
                    'python "$NEBULA_DIR/launcher_wine.py" ' + game_name + ' "' + win_exe + '"']
                else:
                    start_lines = ['#!/bin/bash\n',
                    'python "$NEBULA_DIR/launcher_wine.py" ' + game_name + ' "' + win_exe + '"']

                start_file_path = install_dir + '/' + game_name + '/start.sh'
                start_file = open(start_file_path, 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + start_file_path)

        if parser.has_option(game_name, 'win_settings_exe'):
            win_settings_exe = parser.get(game_name, 'win_settings_exe')
            if win_settings_exe != '':
                print("Writing settings.sh")

                settings_lines = ['#!/bin/bash\n',
                'cd "$INSTALL_DIR/' + game_name + '/game"\n',
                '"$WINELOADER" "' + win_settings_exe + '"']

                settings_file_path = install_dir + '/' + game_name + '/settings.sh'
                settings_file = open(settings_file_path, 'w')
                for line in settings_lines:
                    settings_file.write(line)
                settings_file.close()
                os.system('chmod +x ' + settings_file_path)

        if parser.has_option(game_name, 'winetricks'):
            winetricks = parser.get(game_name, 'winetricks')
            if winetricks != '':
                print("Writing additions.sh")

                additions_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/dialogs.py" "progress" "' + 'winetricks --gui ' + winetricks + '"\n']

                additions_file_path = install_dir + '/' + game_name + '/additions.sh'
                additions_file = open(additions_file_path, 'w')
                for line in additions_lines:
                    additions_file.write(line)
                additions_file.close()
                os.system('chmod +x ' + additions_file_path)

        if parser.has_option(game_name, 'dos_iso'):
            dos_iso = parser.get(game_name, 'dos_iso')
        else:
            dos_iso = ''

        if parser.has_option(game_name, 'dos_exe'):
            dos_exe = parser.get(game_name, 'dos_exe')
            if dos_exe != '':
                print("Writing start.sh")

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_dosbox.py" ' + game_name]

                exe_dir = ''
                if '\\' in dos_exe:
                    exe = dos_exe.split('\\')[-1]
                    exe_dir = '\\'.join(dos_exe.split('\\')[:-1])
                    dos_exe = exe

                start_file_path = install_dir + '/' + game_name + '/start.sh'
                start_file = open(start_file_path, 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + start_file_path)

                game_conf_lines = ['[autoexec]\n',
                '@echo off\n',
                'mount c ' + os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name + '\n',
                'c:\n',
                'imgmount d ' + os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name + '/' + dos_iso + ' -fs iso\n',
                'cls\n',
                'cd ' + exe_dir + '\n',
                dos_exe + '\n',
                'exit\n']

                if dos_iso == '':
                    del game_conf_lines[4]
                    if exe_dir == '':
                        del game_conf_lines[5]
                elif exe_dir == '':
                    del game_conf_lines[6]

                dosbox_game_conf_path = install_dir + '/' + game_name + '/dosbox_game.conf'
                dosbox_game_conf = open(dosbox_game_conf_path, 'w')
                for line in game_conf_lines:
                    dosbox_game_conf.write(line)
                dosbox_game_conf.close()

        if parser.has_option(game_name, 'dos_settings_exe'):
            dos_settings_exe = parser.get(game_name, 'dos_settings_exe')
            if dos_settings_exe != '':
                print("Writing dosbox_settings.conf")

                exe_dir = ''
                if '\\' in dos_settings_exe:
                    exe = dos_settings_exe.split('\\')[-1]
                    exe_dir = '\\'.join(dos_settings_exe.split('\\')[:-1])
                    dos_settings_exe = exe

                settings_conf_lines = ['[autoexec]\n',
                '@echo off\n',
                'mount c ' + os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name + '\n',
                'c:\n',
                'imgmount d ' + os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name + '/' + dos_iso + ' -fs iso\n',
                'cls\n',
                'cd ' + exe_dir + '\n',
                dos_settings_exe + '\n',
                'exit\n']

                if dos_iso == '':
                    del settings_conf_lines[4]
                    if exe_dir == '':
                        del settings_conf_lines[5]
                if exe_dir == '':
                    del settings_conf_lines[6]

                dosbox_settings_conf_path = install_dir + '/' + game_name + '/dosbox_settings.conf'
                dosbox_settings_conf = open(dosbox_settings_conf_path, 'w')
                for line in settings_conf_lines:
                    dosbox_settings_conf.write(line)
                dosbox_settings_conf.close()

        if parser.has_option(game_name, 'scummvm_name') and \
                parser.has_option(game_name, 'scummvm_id'):

            scummvm_name = parser.get(game_name, 'scummvm_name')
            scummvm_id = parser.get(game_name, 'scummvm_id')

            if scummvm_id != '':
                print("Writing start.sh")

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_scummvm.py" ' + game_name + ' ' + scummvm_name]

                start_file_path = install_dir + '/' + game_name + '/start.sh'
                start_file = open(start_file_path, 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + start_file_path)

                scummvmrc_lines = ['[' + scummvm_name + ']\n',
                'gameid=' + scummvm_id + '\n']

                scummvmrc_path = install_dir + '/' + game_name + '/scummvmrc'
                scummvmrc = open(scummvmrc_path, 'w')
                for line in scummvmrc_lines:
                    scummvmrc.write(line)
                scummvmrc.close()

        if parser.has_option(game_name, 'special'):
            commands_list = parser.get(game_name, 'special').split('; ')
            for command in commands_list:
                os.system(command)

        if parser.has_option(game_name, 'win_reg1'):
            win_reg1 = parser.get(game_name, 'win_reg1')
            if win_reg1 != '':
                print("Writing additions.sh, reg keys")

                options_list = parser.options(game_name)

                for i in range(len(options_list)):
                    if options_list[i] == 'win_reg1':
                        win_reg1_index = i

                reg_list = parser.options(game_name)[win_reg1_index:]

                additions_file_path = install_dir + '/' + game_name + '/additions.sh'

                if (parser.has_option(game_name, 'winetricks')) and (winetricks != ''):
                    additions_file = open(additions_file_path, 'a')
                else:
                    additions_file = open(additions_file_path, 'w')
                    additions_file.write('#!/bin/bash\n')

                for item in reg_list:

                    key = parser.get(game_name, item).split('; ')[0]
                    value = parser.get(game_name, item).split('; ')[1]
                    dtype = parser.get(game_name, item).split('; ')[2]
                    data = parser.get(game_name, item).split('; ')[3]

                    line = '"$WINELOADER" reg add "' + key + '" /v "' + value + '" /t ' + dtype + ' /d "' + data + '" /f\n'

                    additions_file.write(line)

                additions_file.close()
                os.system('chmod +x ' + additions_file_path)

if __name__ == "__main__":
    import sys
    autosetup(sys.argv[1], sys.argv[2], sys.argv[3])
