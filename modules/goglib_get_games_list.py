import os, subprocess

def goglib_get_games_list():

    proc = subprocess.Popen(['lgogdownloader', '--exclude', \
    '1,2,4,8,16,32', '--list-details'],stdout=subprocess.PIPE)
    games_detailed_list = proc.stdout.readlines()
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode == 0:

        file_path = os.getenv('HOME') + '/.games_nebula/config/games_list'

        games_list_file = open(file_path, 'w')

        for line in games_detailed_list:
            if 'Getting game info' not in line:
                games_list_file.write(line)

        return 0

    else:

        return 1

if __name__ == "__main__":
    import sys
    goglib_get_games_list()
