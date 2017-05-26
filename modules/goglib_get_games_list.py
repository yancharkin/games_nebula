import os, subprocess

def goglib_get_games_list():
    
    all_games = get_all_games()
    linux_games = get_linux_games()
    
    if (all_games != 0) or (linux_games != 0):
        return 1
    else:
        return 0

def get_all_games():

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

def get_linux_games():

    proc = subprocess.Popen(['lgogdownloader', '--exclude', \
    '1,2,4,8,16,32', '--platform', '4', '--list'],stdout=subprocess.PIPE)
    linux_games_list = proc.stdout.readlines()
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode == 0:

        file_path = os.getenv('HOME') + '/.games_nebula/config/linux_games_list'

        games_list_file = open(file_path, 'w')

        for line in linux_games_list:
            games_list_file.write(line)

        return 0

    else:

        return 1

if __name__ == "__main__":
    import sys
    goglib_get_games_list()
