import socket

def goglib_available():
    try:
        host = socket.gethostbyname("www.gog.com")
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

if __name__ == "__main__":
    import sys
    goglib_available()
