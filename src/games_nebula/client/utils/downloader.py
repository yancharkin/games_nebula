import urllib.request
import urllib.parse
import os
import logging
import signal

from games_nebula.client.translator import _tr

class Downloader:
    """Downloader that can preallocate space and resume donwload."""

    def __init__(self):
        self.__logger = logging.getLogger(__name__)

    def download(self, url, dest_dir, file_name=None,
            block_size=1024**2, timeout=30, preallocate=False, resume=False):
        """Start downloading a file."""

        def timeout_signal(signum, frame):
            raise self.__TimeoutException("Time out.")
        if timeout != -1:
            signal.signal(signal.SIGALRM, timeout_signal)
            signal.alarm(timeout)
        self.__logger.info(_tr("Preparing download. Sending request."))
        try:
            if resume:
                self.__prepare_resume_download(url, dest_dir, file_name, block_size)
                if self.file_size == self.downloaded:
                    self.__logger.info(_tr("The file is already completely downloaded."))
                    return True # download successful
            else:
                self.__prepare_download(url, dest_dir, file_name, block_size)
        except self.__TimeoutException as e:
            self.__logger.error(e)
            return False # download failed
        except Exception as e:
            self.__logger.error(e)
            return False # download failed
        signal.alarm(0)
        if self.file_size:
            self.__logger.info(_tr("Checking available space."))
            free_space = self.__get_free_space()
            if (free_space - self.downloaded) < self.file_size:
                self.__logger.warning(
                        _tr("Not enough space for") +  f' "{self.file_name}"; ' + \
                        _tr("Available") + f': {free_space}; ' + \
                        _tr("Required") + f': {self.file_size}'
                )
                return
            if preallocate:
                if not resume:
                    self.__preallocate_space()
                placeholder = open(f'{self.file_path}.placeholder', 'a')

        self.__logger.info(_tr("Download started."))
        if resume:
            f = open(self.file_path, 'ab')
        else:
            f = open(self.file_path, 'wb')
        while True:
            chunk = self.response.read(self.block_size)
            if not chunk:
                self.__show_progress(self.downloaded, done=True)
                break
            self.downloaded += len(chunk)
            if preallocate and self.file_size:
                placeholder.truncate(self.file_size - self.downloaded)
            f.write(chunk)
            self.__show_progress(self.downloaded)
        print()
        f.close()
        if preallocate and self.file_size:
            placeholder.close()
            os.remove(f'{self.file_path}.placeholder')

        self.__logger.info(_tr("Download completed."))
        return True

    def __set_file_name_and_path(self, file_name, dest_dir, url):
        self.dest_dir = dest_dir
        if file_name:
            self.file_name = file_name
        else:
            try:
                self.file_name = self.response.getheader('Content-Disposition').split('filename=')[1]
            except:
                #self.file_name = url.split('/')[-1]
                url_unquoted = urllib.parse.unquote(url, encoding='utf-8', errors='replace')
                self.file_name = url_unquoted.split('path=')[1].split('/')[-1].split('&token=')[0]
        self.file_path = f'{self.dest_dir}/{self.file_name}'

    def __set_file_size(self):
        try:
            self.file_size = int(self.response.getheader('Content-length'))
        except:
            self.file_size = 0

    def __set_block_size(self, block_size):
        if block_size:
            self.block_size = block_size
        else:
            self.block_size = 8192
            if self.file_size > 1024**2:
                self.block_size = 1024**2

    def __prepare_common(self, url, dest_dir, file_name, block_size):
        self.response = urllib.request.urlopen(url)
        self.__set_file_name_and_path(file_name, dest_dir, url)
        self.__set_file_size()
        self.__set_block_size(block_size)

    def __prepare_download(self, url, dest_dir, file_name, block_size):
        self.__prepare_common(url, dest_dir, file_name, block_size)
        self.downloaded = 0
        if (dest_dir != '.') and (not os.path.exists(dest_dir)):
            os.makedirs(dest_dir)

    def __prepare_resume_download(self, url, dest_dir, file_name, block_size):
        self.__prepare_common(url, dest_dir, file_name, block_size)
        self.downloaded = os.path.getsize(self.file_path)
        if self.file_size == self.downloaded:
            return # already downloaded
        #self.downloaded = os.path.getsize(os.path.abspath(self.file_path))
        request = urllib.request.Request(url)
        request.add_header('Range',f'bytes={self.downloaded}-')
        self.response = urllib.request.urlopen(request)

    def __show_progress(self, downloaded, done=False):
        if not done:
            status = _tr("Downloading")
        else:
            status = _tr("Downloaded")
        unit = 'MB'
        downloaded = downloaded/1024**2
        if self.file_size:
            file_size = self.file_size/1024**2
            if file_size > 1024:
                unit = 'GB'
                file_size = file_size/1024
                downloaded = downloaded/1024
            percents = downloaded*100./file_size
            print('\033[2K', end='')
            print(
                    (
                        f'\r[{status}]'
                        f' [{percents:.0f}%]'
                        f' [{downloaded:.2f}{unit}/{file_size:.2f}{unit}]'
                        f' {self.file_name}'
                    ),
                    end = '', flush = True
            )
        else:
            print(
                    (
                        f'\r[{status}] {self.file_name} [{downloaded:.2f} {unit}]'
                    ),
                    end = '', flush = True
            )

    def __get_free_space(self):
        stats = os.statvfs(self.dest_dir)
        return stats.f_bavail * stats.f_frsize

    def __preallocate_space(self):
        self.__logger.info(_tr("Preallocating space."))
        mb = 1024**2
        chunk = os.urandom(mb)
        chunk_size = mb
        if self.file_size < mb:
            chunk = b'\0'
            chunk_size = 1
        with open(f'{self.file_path}.placeholder', 'wb') as f:
            current_size = 0
            while current_size < (self.file_size - self.downloaded):
                f.write(chunk)
                current_size += chunk_size

    class __TimeoutException(Exception):
        def __init__(self, __TimeoutException): pass
