from .simpledbf import Dbf5
import socket
import sys

__all__ = ['Dbf5', ]


hostname = socket.gethostname()

if sys.platform == 'win32':
    CONNECTION = {'database': 'DI','user': 'postgres', 'password':'postgres', 'host': 'localhost', 'port': 5432}
    path = r"C:\Test.Zakupki.local\kladr"
    patool = r"C:\Python34\Scripts\patool"
    ssrf_path = r"C:\Test.Zakupki.local\ssrf"
elif sys.platform == 'linux':
    if hostname == 'esb':
        CONNECTION = 
        path = '/opt/storage/temp/kladr'
        patool = '/usr/local/bin/patool'
        ssrf_path = '/opt/storage/temp/ssrf'
    elif hostname == 'test-esb':
        CONNECTION = 
        path = '/storage/temp/kladr'
        patool = '/usr/local/bin/patool'
        ssrf_path = '/storage/temp/ssrf'
