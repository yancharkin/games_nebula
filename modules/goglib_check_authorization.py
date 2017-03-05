import subprocess

def goglib_authorized():

    proc = subprocess.Popen(['lgogdownloader', '--list'],stdout=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode == 0:
        return True
    else:
        return False

if __name__ == "__main__":
    import sys
    goglib_authorized()
