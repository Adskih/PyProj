import logging, traceback
import sys
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def write_log(self, *args):
        pass


class LoggerDb(Logger):
    LOG_FORMATTER = '%(asctime)s|%(levelname)s|%(message)s'

    def __init__(self, log_name, log_file, job, level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        formatter = logging.Formatter(self.LOG_FORMATTER)
        filehandler = logging.FileHandler(log_file)
        filehandler.setFormatter(formatter)
        self.job = job
        self.logger.setLevel(level)
        self.logger.addHandler(filehandler)

    def write_log(self, action, table, id_column, filename, xpath):
        self.logger.info('%s_loader|%s|%s|__id=%s|%s|xpath=%s' % (self.job, action, table, id_column, filename, xpath))

    def write_warning(self, action):
        self.logger.warn("Protocol_loader|%s" % action)

    def write_extra_log(self, data):
        self.logger.info(data)

    def close_log(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


class LoggerTrace(LoggerDb, Logger):

    def __init__(self, log_name, log_file, job, level=logging.INFO):
        LoggerDb.__init__(self, log_name, log_file, job, level=logging.INFO)
        formatter = logging.Formatter(self.LOG_FORMATTER)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        self.job = job

        def my_handler(type, value, tb):
            self.logger.error("Uncaught exception: {0}|{1}".format(str(value), ''.join(traceback.format_tb(tb))))

        # Install exception handler
        sys.excepthook = my_handler

    def write_log(self, action, *args):
        self.logger.info("%s_loader|%s" % (self.job, action))

    def close_log(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

if __name__=='__main__':
    logger = LoggerDb(log_file=r'C:\test1', log_name='Protocol_loader', job='Protocol')
    logger.write_log('UPDATE', 'public.table', '555', 'c:\\filename.txt', 'root/child/child[11]')
    logger1 = LoggerTrace(log_file=r'C:\test2', log_name='parser1', job='EGRUL')
    logger1.write_log('File: loaded')
    logger1.close_log()
