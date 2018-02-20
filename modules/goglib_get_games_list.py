import os, subprocess, sys

def b2str(b):
    if sys.version_info[0] == 2:
        return str(b)
    elif sys.version_info[0] == 3:
        return b.decode('utf-8')

def goglib_get_games_list():

    proc = subprocess.Popen(['lgogdownloader', '--exclude', \
    '1,2,4,8,16,32', '--list-details'],stdout=subprocess.PIPE)
    games_detailed_list = proc.stdout.readlines()
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode == 0:

        file_path = os.getenv('HOME') + '/.games_nebula/config/games_list'

        games_list_file = open(file_path, 'w')

        for line in games_detailed_list:
            if 'Getting game info' not in line.decode('utf-8'):
                games_list_file.write(b2str(line))

        return 0

    else:

        return 1

if __name__ == "__main__":
    import sys
    goglib_get_games_list()
