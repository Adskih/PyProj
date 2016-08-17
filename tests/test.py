from model_pckg.model import RegistrySsrf
import urllib3
import socket
import sys
import os
from pyunpack import Archive
from simpledbf import patool
hostname = socket.gethostname()
from dateutil.parser import parse

if sys.platform == 'win32':
    path = r"C:\Test.Zakupki.local\ssrf"
elif sys.platform == 'linux':
    if hostname == 'esb':
        path = '/opt/storage/temp/ssrf'
    elif hostname == 'test-esb':
        path = '/storage/temp/ssrf'
else:
    path = None


archive_path = os.path.join(path, 'SSRF.ARJ')

http = urllib3.PoolManager()
r = http.request('GET', "http://www.gnivc.ru/html/gnivcsoft/ssrf/SSRF.ARJ", preload_content=False)  # Скачиваем архив с сайта
with open(archive_path, 'wb') as file:
   file.write(r.data)  # Сохраняем скаченный архив
r.release_conn()

Archive(archive_path).extractall(path, patool_path=patool, auto_create_dir=True) # Распаковываем архив в дректорию
os.remove(archive_path)  # После удаляем

file_path = os.path.join(path, 'SSRF.TXT')
with open(file_path, 'r', encoding='cp866') as data:
    line_array = list(data)

actuality = parse(line_array[0].split('|')[1])

for line in line_array[1:]:
    region_code = line.split('|')[0]
    region_name = line.split('|')[1]
    try:
        record = RegistrySsrf.select().where(RegistrySsrf.code == region_code).get()
        record.name = region_name
        record.actuality = actuality

    except RegistrySsrf.DoesNotExist:
        record = RegistrySsrf(code=region_code, name=region_name, actuality=actuality)
    record.save()
os.remove(file_path)







