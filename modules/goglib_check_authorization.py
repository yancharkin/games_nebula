import subprocess, os

def goglib_authorized():

    dev_null = open(os.devnull, 'w')
    proc = subprocess.Popen(['lgogdownloader'], stdout=dev_null, \
        stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    dev_null.close()

    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode == 0:
        print("Authorized on GOG")
        return True
    else:
        print("Not authorized on GOG")
        return False

if __name__ == "__main__":
    import sys
    goglib_authorized()
