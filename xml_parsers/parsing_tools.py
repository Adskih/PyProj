"""
Функции для обработки данных из xml
"""
import datetime
from dateutil.parser import parse
import re
from enum import Enum, unique

@unique
class Types(Enum):
    string = 1
    date = 2
    number = 3
    bool = 4


class ParsingTools():

    non_decimal = re.compile(r'[^\d.]+')
    CHAR_PATTERN = re.compile(r'[\d]+|^-+$|^.\.?$')

    @staticmethod
    def emptyToNull(string):
        if string:
            string = string.strip()
            if string != '':
                return string
            else:
                return None
        else:
            return None

    @staticmethod
    def person_name(string):
        if string:
            result = ParsingTools.CHAR_PATTERN.sub('', string)
            return ParsingTools.emptyToNull(result.strip())
        else:
            return None

    @staticmethod
    def get_node_name(root):
        for child in root:
            return child.tag.split('}')[1]


    @staticmethod
    def get_val_from_node(node, is_date=False, is_bool=False, is_num=False):
        if node:
            if len(node) == 1:
                if is_date:
                    try:
                        parsed_date = parse(node[0].text).replace(tzinfo=None)
                    except (ValueError, TypeError):
                        parsed_date = parse(node[0].text.split('+')[0]).replace(tzinfo=None)
                    return parsed_date
                elif is_bool:
                    return node[0].text.lower() in "true"
                elif is_num:
                    return round(float(node[0].text), 2)
                else:
                    return node[0].text
        else:
            return None

    @staticmethod
    def get_values_from_xml(inst, lxml_obj , xpath_dict, nsmp=None):
        for key in xpath_dict:
            setattr(inst, key, ParsingTools.get_values_from_xmlnode(lxml_obj.xpath(xpath_dict[key]['path'],
                                                                                   namespaces=nsmp),
                                                                    xpath_dict[key]['type']))

    @staticmethod
    def get_values_from_xmlnode(node, type):
        if node:
            if len(node) == 1:
                try:
                    if type == Types.date:
                        try:
                            parsed_date = parse(node[0]).replace(tzinfo=None)
                        except (ValueError, TypeError):
                            parsed_date = parse(node[0].split('+')[0]).replace(tzinfo=None)
                        return parsed_date
                    elif type == Types.bool:
                        return node[0].lower() in "true"
                    elif type == Types.number:
                        return round(float(node[0]), 2)
                    elif type == Types.string:
                        result = node[0]
                        if not isinstance(result, str):
                            raise TypeError
                        else:
                            return result
                except (TypeError, AttributeError):
                    if type == Types.date:
                        try:
                            parsed_date = parse(node[0].text).replace(tzinfo=None)
                        except (ValueError, TypeError):
                            parsed_date = parse(node[0].text.split('+')[0]).replace(tzinfo=None)
                        return parsed_date
                    elif type == Types.bool:
                        return node[0].text.lower() in "true"
                    elif type == Types.number:
                        return round(float(node[0].text), 2)
                    else:
                        return node[0].text
        else:
            return None

    @staticmethod
    def get_xpath(tree, root, path, nsmp=None):
        node = root.xpath(path, namespaces=nsmp)
        if len(node) > 0:
            return tree.getpath(node[0].getparent())
        else:
            return None

    @staticmethod
    def get_actuality(actuality):
        mindate = datetime.datetime(datetime.MINYEAR, 1, 1)
        return actuality or mindate

    @staticmethod
    def compare_two_inst(inst, first_dict, second_dict):
        result_dict = {}
        if inst:
            result_inst = inst.__class__()
        else:
            result_inst = None
        for key in first_dict:
            if second_dict.get(key) is not None and \
                    (ParsingTools.get_actuality(second_dict.get('_actuality')) > ParsingTools.get_actuality(first_dict.get('_actuality'))):
                result_dict[key] = second_dict.get(key)
            elif second_dict.get(key) is not None and \
                    (ParsingTools.get_actuality(second_dict.get('_actuality')) == ParsingTools.get_actuality(first_dict.get('_actuality'))):
                result_dict[key] = second_dict.get(key)
            else:
                result_dict[key] = (first_dict.get(key) or second_dict.get(key))
        if result_inst:
            for key in result_dict:
                result_inst.__dict__['_data'].update({key: result_dict.get(key)})
            return result_inst
        else:
            return result_dict



    @staticmethod
    def check_inn(inn):
        inn = ParsingTools.emptyToNull(inn)
        if inn:
            inn = ParsingTools.non_decimal.sub('', inn)
        else:
            return None

        if len(inn) in (9, 11):
            inn = '0%s' % inn

        if len(inn) not in (10,12) or inn.startswith('00'):
            return None

        def inn_csum(inn):
            k = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
            pairs = zip(k[11 - len(inn):], [int(x) for x in inn])
            return str(sum([k * v for k, v in pairs]) % 11 % 10)

        if len(inn) == 10:
            return inn if inn[-1] == inn_csum(inn[:-1]) else None
        else:
            return inn if inn[-2:] == inn_csum(inn[:-2]) + inn_csum(inn[:-1]) else None

    @staticmethod
    def currency_to_long(currency, index):
        if currency:
            return int(currency*index)
        else:
            return None

    @staticmethod
    def check_kpp(kpp):
        kpp = ParsingTools.emptyToNull(kpp)

        if kpp:
            kpp = ParsingTools.non_decimal.sub('', kpp)
        else:
            return None

        if len(kpp) == 8:
            kpp = '0%s' % kpp

        if len(kpp) == 9 and not kpp.startswith("00"):
            return kpp
        else:
            return None

    @staticmethod
    def check_ogrn(ogrn):
        ogrn = ParsingTools.emptyToNull(ogrn)

        if ogrn:
            ogrn = ParsingTools.non_decimal.sub('', ogrn)
        else:
            return None

        if len(ogrn) != 13 and len(ogrn) != 15:
            return None

        if int(ogrn[0:-1]) % (11 if len(ogrn) == 13 else 13) % 10 == int(ogrn[-1:]):
            return ogrn
        else:
            return None

    @staticmethod
    def check_phone_num(phone):
        phone = ParsingTools.emptyToNull(phone)

        if phone:
            phone = ParsingTools.non_decimal.sub('', phone)
        else:
            return None

        if len(phone)>15 or phone[0:3] in ([str(n)*3 for n in range(0,10)]) or len(phone)<10:
            return None
        else:
            return phone








# Check Block
if __name__ == '__main__':
    print(ParsingTools.get_actuality(None))
    #print(ParsingTools.non_decimal.sub('', '66546546654654   afsdfsfs3333'))
    #print(ParsingTools.emptyToNull('  vvvv'))
    #print(ParsingTools.check_inn('040301191523'))
    #print(ParsingTools.currency_to_long(21321321313123, 100))
#    print(ParsingTools.get_val_from_node(['9894984'], is_num=True))
    #print(ParsingTools.currency_to_long(143200.67, 100))
    #print(ParsingTools.check_kpp('82401001'))
    #print(ParsingTools.check_ogrn('1095407009510'))
    #print('1027739769331'[-1:])
    #print(int('1027739769331'[0:-1]) % (11 if len('1027739769331') == 13 else 13) % 10 == int('1027739769331'[-1:]))
    #print(ParsingTools.currency_to_long(round(float('143200.6700'), 2), 100))
    #print(ParsingTools.check_phone_num('  74956993844 '))

