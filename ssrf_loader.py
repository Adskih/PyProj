#!/usr/bin/env python3
"""
Загрзучик справочника по ssrf
"""
from model_pckg.model import RegistrySsrf
import urllib3
import os
from pyunpack import Archive
from simpledbf import patool, ssrf_path
from dateutil.parser import parse
from datetime import datetime


print('Start job at %s' % datetime.now())
archive_path = os.path.join(ssrf_path, 'SSRF.ARJ')

http = urllib3.PoolManager()
r = http.request('GET', "http://www.gnivc.ru/html/gnivcsoft/ssrf/SSRF.ARJ", preload_content=False)  # Скачиваем архив с сайта
with open(archive_path, 'wb') as file:
   file.write(r.data)  # Сохраняем скаченный архив
r.release_conn()

Archive(archive_path).extractall(ssrf_path, patool_path=patool, auto_create_dir=True)  # Распаковываем архив в дректорию
os.remove(archive_path)  # После удаляем

file_path = os.path.join(ssrf_path, 'SSRF.TXT')
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

print('End job at %s' % datetime.now())