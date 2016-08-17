#!/usr/bin/env python3
"""
Удаляет некорректные данные по извещениям и протоколам
"""
from model_pckg.model import Notifications, Protocols
from loger_pack.logger import LoggerDb
from loger_pack import PROTOCOL_LOG_FILE


stop = False
db_logger = LoggerDb('Data_corrector', PROTOCOL_LOG_FILE, 'Protocols_Notifications_cleaner')
while not stop:
    res = Notifications.select().where(Notifications.lotnumber == None).limit(10000)
    if len(res) != 0:
        for notif in res:
            print(notif._id)
            for protocol in Protocols.select().where(Protocols._notification==notif._id):
                protocol.delete_instance()
                db_logger.write_extra_log('Data_corrector|DELETE|public.protocols|__id=%s' % protocol._id)
            notif.delete_instance()
            db_logger.write_extra_log('Data_corrector|DELETE|public.notifications|__id=%s' % notif._id)
    else:
        stop = True
