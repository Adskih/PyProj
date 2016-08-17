import sys
import socket

hostname = socket.gethostname()

if sys.platform == 'win32':
    ZAKUPKI_ZIP_DIR = r'C:\zip\fcs_regions'
    ZAKUPKI_EXTRACT_DIR = r'C:\Test.Zakupki.local\fcs_regions'
elif sys.platform == 'linux':
    if hostname == 'esb':
        ZAKUPKI_ZIP_DIR = '/opt/storage/FTP.ZAKUPKI.RU/fcs_regions'
        ZAKUPKI_EXTRACT_DIR = '/opt/storage/temp/fcs_regions'
    elif hostname == 'test-esb':
        ZAKUPKI_ZIP_DIR = '/opt/storage/FTP.ZAKUPKI.RU/fcs_regions'
        ZAKUPKI_EXTRACT_DIR = '/storage/temp/fcs_regions'
