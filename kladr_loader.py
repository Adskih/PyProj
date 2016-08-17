#!/usr/bin/env python3
"""
Скрипт-загрузчик КЛАДР
"""
import glob
import os
import psycopg2
import urllib3
from pyunpack import Archive
from simpledbf.simpledbf import Dbf5
from simpledbf import path, patool, CONNECTION
from datetime import datetime

archive_path = os.path.join(path, 'Base.7z')
print('Start job at %s' % datetime.now())
http = urllib3.PoolManager()
r = http.request('GET', "http://www.gnivc.ru/html/gnivcsoft/KLADR/Base.7z", preload_content=False)  # Скачиваем архив с сайта
with open(archive_path, 'wb') as file:
   file.write(r.data)  # Сохраняем скаченный архив
r.release_conn()

print('Archive %s downloaded' % archive_path)

Archive(archive_path).extractall(path, patool_path=patool, auto_create_dir=True) # Распаковываем архив в дректорию
os.remove(archive_path)  # После удаляем

connection = psycopg2.connect(database=CONNECTION['database'], user=CONNECTION['user'], password=CONNECTION['password'],
                              host=CONNECTION['host'], port=CONNECTION['port'])

for file in glob.glob(os.path.join(path, '*.DBF')):
    file_name = os.path.split(file)[1].split('.')[0]
    file_path = os.path.split(file)[0]
    csv_file = os.path.join(file_path, '%s.csv' % file_name)
    try:
        dbf = Dbf5(file,codec='cp866', escape='"')  # Считываем DBF в память
        print('Converting %s to %s' % (file, csv_file))
        dbf.to_csv(csv_file, header=False, na='')  # И сохраняем данные в csv
        cur = connection.cursor()
        with open(csv_file, 'r', encoding='cp866') as f:
           table = (psycopg2.extensions.AsIs("kladr.%s" % file_name.lower()),)
           sql = "TRUNCATE %s;"
           cur.execute(sql, table)  # Чистим таблицу
           cur.copy_expert('COPY %s FROM STDIN (DELIMITER \',\' , FORMAT CSV)' % table, f)  # Заполняем данными таблицу
           print('Data loaded into %s' % table)
           connection.commit()
        os.remove(csv_file)
    except AssertionError:
        print("FILE %s HAS BAD FORMAT!" % file)
    finally:
        del dbf
        os.remove(file)
print('End job at %s' % datetime.now())