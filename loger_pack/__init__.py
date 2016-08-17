import sys

if sys.platform == 'win32':
    PROTOCOL_LOG_FILE = 'C:\\soft\\log\\protocol.log'
    PROTOCOL_LOG_FILE_OUT = 'C:\\soft\\log\\protocol_out.log'
    CONTRACT_LOG_FILE = 'C:\\soft\\log\\contracts.log'
    CONTRACT_LOG_FILE_OUT = 'C:\\soft\\log\\contracts_out.log'
    EGUL_LOG_FILE = 'C:\\soft\\log\\egrul.log'
    EGRUL_LOG_FILE_OUT = 'C:\\soft\\log\\egrul_out.log'
    RNP_LOG_FILE = 'C:\\soft\\log\\rnp.log'
    RNP_LOG_FILE_OUT = 'C:\\soft\\log\\rnp_out.log'
elif sys.platform == 'linux':
    PROTOCOL_LOG_FILE = '/var/log/di/dmj_protocol.log'
    PROTOCOL_LOG_FILE_OUT = '/var/log/di/dmj_protocol_out.log'
    CONTRACT_LOG_FILE = '/var/log/di/dmj_contract.log'
    CONTRACT_LOG_FILE_OUT = '/var/log/di/dmj_contract_out.log'
    EGUL_LOG_FILE = '/var/log/di/dmj_egrul.log'
    EGRUL_LOG_FILE_OUT = '/var/log/di/dmj_egrul_out.log'
    RNP_LOG_FILE = '/var/log/di/dmj_rnp.log'
    RNP_LOG_FILE_OUT = '/var/log/di/dmj_rnp_out.log'
