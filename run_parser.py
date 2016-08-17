#!/usr/bin/env python3
"""Запускает и логирует загрузчики"""
from input_files import ZAKUPKI_ZIP_DIR
from input_files.file_worker import Zipper
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-j', '--job', help='Parser to run')
args = parser.parse_args()

if __name__ == '__main__':
    run = Zipper(ZAKUPKI_ZIP_DIR, args.job)
    print('End of work at', datetime.datetime.now())


