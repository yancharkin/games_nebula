import os
import subprocess
import shutil
import zlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

nebula_dir = os.getenv('NEBULA_DIR')

def simple_message(message_type, text_1, text_2):
    """Show simple message box"""
    message_dialog = Gtk.MessageDialog(
        None,
        0,
        message_type,
        Gtk.ButtonsType.OK,
        text_1
    )

    message_dialog.format_secondary_text(text_2)
    content_area = message_dialog.get_content_area()
    content_area.set_property('margin-left', 10)
    content_area.set_property('margin-right', 10)
    content_area.set_property('margin-top', 10)
    content_area.set_property('margin-bottom', 10)

    try:
        content_area_label = content_area.get_children()[0].get_children()[0].get_children()[1]
        content_area_label.set_property('justify', Gtk.Justification.CENTER)
    except AttributeError:
        content_area_label = content_area.get_children()[0].get_children()[1].get_children()[1]
        content_area_label.set_property('justify', Gtk.Justification.CENTER)
    except:
        pass

    message_dialog.run()
    message_dialog.destroy()

def ext_innounp(file_path, dest_dir):
    """Unpack installer using innounp and wine"""
    def get_files_info(dest_dir):
        if sys.version_info[0] == 3:
            with open(dest_dir + 'install_script.iss', 'r', encoding='utf-8') as f:
                raw_data = f.read().splitlines()
        else:
            with open(dest_dir + 'install_script.iss', 'r') as f:
                raw_data = f.read().splitlines()

        files_dict = {}
        chunks_dict = {}
        files_chunks_dict = {}
        for i in range(len(raw_data)):
            if ('Source: ' in raw_data[i]) and ('BeforeInstall: ' in raw_data[i]):
                temp_list = raw_data[i].split('; ')
                file_src = temp_list[0].split(': ')[1].replace('"', '').replace('\\', '/')
                file_dest = temp_list[3].split(': ')[1].replace('"', '').split(', ')[1].replace("'", '')
                files_dict[file_dest] = file_src
                chunks_n = int(temp_list[3].split(': ')[1].replace('"', '').split(', ')[2].strip(')'))
                if chunks_n != 1:
                    chunks_list = []
                    for j in range(1, chunks_n):
                        temp_list = raw_data[i+j].split('; ')
                        chunk_src = temp_list[0].split(': ')[1].replace('"', '').replace('\\', '/')
                        chunk_dest = temp_list[3].split(': ')[1].split(', ')[0].replace('"after_install(', '').replace('"after_install_dependency(', '').replace("'", '')
                        chunks_dict[chunk_dest] = chunk_src
                        chunks_list.append(chunk_dest)
                    files_chunks_dict[file_dest] = chunks_list

        return files_dict, chunks_dict, files_chunks_dict

    def decompress_files(files_dict, dest_dir):
        for file_path in files_dict:
            full_file_path = dest_dir + file_path
            file_path_dir = os.path.dirname(full_file_path)
            file_name = os.path.basename(full_file_path)
            src_path = dest_dir + files_dict[file_path]
            print('Decompressing: ' + file_name)
            if not os.path.exists(file_path_dir):
                os.makedirs(file_path_dir)
            with open(src_path, 'rb') as comp_file, \
                    open(full_file_path, 'wb') as decomp_file:
                comp_data = comp_file.read()
                decomp_data = zlib.decompress(comp_data)
                decomp_file.write(decomp_data)

    def append_chunks(files_chunks_dict, dest_dir):
        for file_path in files_chunks_dict:
            for chunk in files_chunks_dict[file_path]:
                print('Appending chunk to: ' + os.path.basename(file_path))
                full_file_path = dest_dir + file_path
                full_chunk_path = dest_dir + chunk
                with open(full_chunk_path, 'rb') as chunk_file, \
                        open(full_file_path, 'ab') as cur_file:
                    chunk = chunk_file.read()
                    cur_file.write(chunk)
                os.remove(full_chunk_path)

    innounp = nebula_dir + '/bin/innounp.exe'
    os.environ['WINEDEBUG'] = '-all'
    os.environ['WINEPREFIX'] = os.getenv('HOME') + '/.games_nebula/wine_prefix'

    subprocess.call(['wine', innounp, '-y', '-x', file_path, '-d' + dest_dir])

    files_dict, \
    chunks_dict, \
    files_chunks_dict = get_files_info(dest_dir)

    if len(files_dict) > 0:
        decompress_files(files_dict, dest_dir)
        decompress_files(chunks_dict, dest_dir)
        append_chunks(files_chunks_dict, dest_dir)

    commonappdata_dir = dest_dir + '{commonappdata}'
    app_dir = dest_dir + '{app}'
    app_dir_new = dest_dir + 'app'
    game_dir = dest_dir + '{game}'
    game_dir_new = dest_dir + 'game'
    tmp_dir = dest_dir + '{tmp}'
    tmp_dir_new = dest_dir + 'tmp'

    if os.path.exists(commonappdata_dir): shutil.rmtree(commonappdata_dir)
    if os.path.exists(app_dir): os.rename(app_dir, app_dir_new)
    if os.path.exists(game_dir): os.rename(game_dir, game_dir_new)
    if os.path.exists(tmp_dir): os.rename(tmp_dir, tmp_dir_new)

def ext_innoextact(file_path, dest_dir):
    """Unpack installer using innoextract"""
    if os.path.exists(nebula_dir + '/bin/innoextract'):
        innoextract = nebula_dir + '/bin/innoextract'
    else:
        innoextract = 'innoextract'
    subprocess.call([innoextract, '--gog', file_path, '-d', dest_dir])

def ext_wine(file_path, dest_dir):
    """Unpack installer using wine"""
    wineprefix_path = dest_dir + '/wine_prefix'
    os.environ['WINEPREFIX'] = wineprefix_path
    os.environ['WINEDEBUG'] = '-all'
    os.environ['WINEDLLOVERRIDES'] = 'mshtml,mscoree=d'
    if not os.path.exists(wineprefix_path):
        os.makedirs(wineprefix_path)
    dest_dir = dest_dir + '/game'
    proc = subprocess.Popen(['winepath', '-w', dest_dir], stdout=subprocess.PIPE)
    dest_dir_win = proc.stdout.readline().decode('utf-8').strip()
    subprocess.call([
            'wine',
            file_path,
            '/DIR=' + dest_dir_win,
            '/VERYSILENT',
            '/SUPPRESSMSGBOXES'
    ])
    if not os.path.exists(dest_dir):
        simple_message(
            Gtk.MessageType.INFO,
            "Info",
            "Do not change the installation path!"
        )
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        subprocess.call([
                'wine',
                file_path,
                '/LANG=english',
                '/DIR=' + dest_dir_win,
        ])

def ext_unzip(file_path, dest_dir):
    """Unpack installer using unzip"""
    subprocess.call([
            'unzip', '-o',
            file_path,
            '-d',
            dest_dir
    ])

def extract(file_path, dest_dir, *args):
    """Main function"""
    installer_type = args[0][0]
    if installer_type == 'exe':
        ext_wine(file_path, dest_dir)
    elif installer_type == 'sh':
        ext_unzip(file_path, dest_dir)

if __name__ == '__main__':
    import sys
    extract(sys.argv[1], sys.argv[2], sys.argv[3:])
