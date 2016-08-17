from xml_parsers.parsing_tools import ParsingTools


class InnChecker:
    def __get__(self, instance, owner):
        print('Getting inn')
        return instance.inn

    def __set__(self, instance, val):
        print('Setting inn')
        instance.inn = ParsingTools.check_inn(val)

class OgrnChecker:
    def __get__(self, instance, owner):
        print('Getting ogrn')
        return instance.ogrn

    def __set__(self, instance, val):
        print('Setting ogrn')
        instance.ogrn = ParsingTools.check_ogrn(val)

class KppChecker:
    def __get__(self, instance, owner):
        return instance.kpp

    def __set__(self, instance, val):
        instance.kpp = ParsingTools.check_kpp(val)