import os
import subprocess
import shutil
import zlib

nebula_dir = os.getenv('NEBULA_DIR')

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

def innounp(file_path, dest_dir):

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

def innoextact(file_path, dest_dir):

    if os.path.exists(nebula_dir + '/bin/innoextract'):
        innoextract = nebula_dir + '/bin/innoextract'
    else:
        innoextract = 'innoextract'

    subprocess.call([innoextract, '--gog', file_path, '-d', dest_dir])

def extract(file_path, dest_dir, *args):

    if dest_dir[-1] != '/': dest_dir += '/'

    #~ # Process additional args (if needed)
    #~ if len(args[0]) > 0: pass

    if os.path.exists(nebula_dir + '/bin/innounp.exe'):
        innounp(file_path, dest_dir)
    else:
        innoextact(file_path, dest_dir)

if __name__ == '__main__':
    import sys
    extract(sys.argv[1], sys.argv[2], sys.argv[3:])
