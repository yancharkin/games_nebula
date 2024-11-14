import os
from zipfile import ZipFile
import logging

from games_nebula.client.translator import _tr
from games_nebula.client.utils import convert_from_bytes

class Unzipper:
    """Wrapper aroud ZipArchive class for easier extraction"""

    __logger = logging.getLogger(__name__)
    def extract(self, file_path, output_dir):
        """Extract all files from a zip file showing progress."""
        zip_archive = ZipArchive(file_path)
        zip_archive.extract(output_dir)

    def get_size(self, file_path):
        """Return uncompressed size of all files in the zip file."""
        zip_archive = ZipArchive(file_path)
        return zip_archive.get_size()

class ZipArchive:
    """Class for working with a single zip file."""

    __logger = logging.getLogger(__name__)
    def __init__(self, zip_archive_path):
        self.__zip_archive = ZipFile(zip_archive_path)

    def extract(self, output_dir):
        """Extract all files from a zip file showing progress."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        free_disk_space = self.__get_free_space(output_dir)
        total_uncompressed_size = self.get_size()
        if total_uncompressed_size > free_disk_space:
            available = convert_from_bytes(free_disk_space)
            required = convert_from_bytes(total_uncompressed_size)
            __logger.warning(
                    _tr("Not enough disk space.") + '; ' + \
                    _tr("Available") + f': {available[0]} {available[1]}; ' + \
                    _tr("Required") + f': {required[0]} {required[1]}'
            )
            os.removedirs(output_dir)
            return
        symlinks = {}
        directories = []
        bytes_extracted = 0
        for file_info in self.__zip_archive.filelist:
            zipped_file_path = file_info.filename
            attr = file_info.external_attr
            if  attr == 2717843456:
                target_file = self.__zip_archive.read(zipped_file_path).decode('utf-8')
                symlink = f'{output_dir}/{zipped_file_path}'
                symlinks[symlink] = target_file
            elif (attr == 1106051088) or (self.__zip_archive.getinfo(zipped_file_path).is_dir()):
                directories.append(zipped_file_path)
            else:
                attr = attr >> 16
                extracted_file_path = f'{output_dir}/{zipped_file_path}'
                # ZipFile's extract method not used because it is not showing progress
                bytes_extracted = self.__extract_file(total_uncompressed_size,
                        bytes_extracted, zipped_file_path, extracted_file_path
                )
                os.chmod(extracted_file_path, attr)
        print()
        for symlink in symlinks:
            if not os.path.exists(symlink):
                os.symlink(symlinks[symlink], symlink)
        for directory in directories:
            if not os.path.exists(f'{output_dir}/{directory}'):
                os.makedirs(f'{output_dir}/{directory}')

    def get_size(self):
        """Return uncompressed size of all files in the zip file."""
        size = 0
        for f in self.__zip_archive.filelist:
            size += f.file_size
        return size

    def __get_free_space(self, output_dir):
        stats = os.statvfs(output_dir)
        return stats.f_bavail * stats.f_frsize

    def __extract_file(self, total_uncompressed_size,
            bytes_extracted, zipped_file_path, extracted_file_path):
        if not os.path.exists(os.path.dirname(extracted_file_path)):
            os.makedirs(os.path.dirname(extracted_file_path))
        block_size = 8192
        file_size = self.__zip_archive.getinfo(zipped_file_path).file_size
        if file_size > 1024**2:
            block_size = 1024**2
        zipped_file = self.__zip_archive.open(zipped_file_path)
        unzipped_file = open(extracted_file_path, 'wb')
        while True:
            chunk = zipped_file.read(block_size)
            if not chunk:
                self.__show_progress(bytes_extracted,
                        total_uncompressed_size, zipped_file_path, done=True)
                break
            bytes_extracted += len(chunk)
            unzipped_file.write(chunk)
            self.__show_progress(bytes_extracted, total_uncompressed_size, zipped_file_path)
        zipped_file.close()
        unzipped_file.close()
        return bytes_extracted

    def __show_progress(self, bytes_extracted,
            total_uncompressed_size, zipped_file_path, done=False):
        if not done:
            currently_processing = os.path.basename(zipped_file_path)
            status = _tr("Installing")
        else:
            currently_processing = ''
            status = _tr("Installed")
        percents = bytes_extracted*100./total_uncompressed_size
        total_size = convert_from_bytes(total_uncompressed_size)
        unit = total_size[1]
        extracted = convert_from_bytes(bytes_extracted, unit=unit)
        print('\033[2K', end='')
        print(
                (
                    f'\r[{status}]'
                    f' [{percents:.0f}%]'
                    f' [{extracted[0]}{unit}/{total_size[0]}{unit}]'
                    f' {currently_processing}'
                ),
                end = '', flush = True
        )
