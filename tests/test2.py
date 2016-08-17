import lxml.etree as etree
tree = etree.parse(r'C:\Test.Zakupki.local\EGRUL_2015-11-25_49977.XML')
from xml_parsers.parsing_tools import Types
xpath_dict = {
    'ogrn': {'path': './@ОГРН', 'parg': 'str'},
    'inn': {'path': './ИНН@', 'parg': 'str'},
    'kpp': {'path': './КПП@', 'parg': 'str'},
    'ogrn_date': {'path': './ДатаОГРН@', 'parg': 'date'},
    'okopf_code': {'path': './КодОПФ@', 'parg': 'str'},
    'actuality': {'path': './ДатаВып@', 'parg': 'date'}
}
#root = tree.getroot()
#for child in root:
 #   t = child.xpath('./@ОГРН')[0]
 #   print(tree.getpath(t.getparent()))
  #  #print(child.xpath('./@ОГРН', namespaces=None))
l = [{
            'f_flegal_inn': {'path': './НаимИННЮЛ/@ИНН', 'type': Types.string},
            'f_flegal_ogrn': {'path': './НаимИННЮЛ/@ОГРН', 'type': Types.string},
            'f_flegal_fulltitle': {'path': './НаимИННЮЛ/@НаимЮЛПолн', 'type': Types.string},
            'f_flegal_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_flegal_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number}
        },
    {
            'f_gmu_fulltitle': {'path': './ВидНаимУчр/@НаимМО', 'type': Types.string},
            'f_gmu_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_gmu_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number},
            'f_gmu_region_code': {'path': './ВидНаимУчр/@КодРегион', 'type': Types.string},
            'f_gmu_region_name': {'path': './ВидНаимУчр/@НаимРегион', 'type': Types.string},
            'external_inn': {'path': './СвОргОсущПр/НаимИННЮЛ/@ИНН', 'type': Types.string},
            'external_ogrn': {'path': './СвОргОсущПр/НаимИННЮЛ/@ОГРН', 'type': Types.string},
            'external_fulltitle': {'path': './СвОргОсущПр/НаимИННЮЛ/@НаимЮЛПолн', 'type': Types.string}
        }, {
            'f_pif_fulltitle': {'path': './СвНаимПИФ/@НаимПИФ', 'type': Types.string},
            'f_pif_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_pif_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number},
            'manage_inn': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@ИНН', 'type': Types.string},
            'manage_ogrn': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@ОГРН', 'type': Types.string},
            'manage_fulltitle': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@НаимЮЛПолн', 'type': Types.string}
        }, {
            'filial_kpp': {'path': './СвУчетНОФилиал/@КПП', 'type': Types.string},
            'filial_fulltitle': {'path': './СвНаим/@НаимПолн', 'type': Types.string}
        }, {
            'podrazd_kpp': {'path': './СвУчетНОПредстав/@КПП', 'type': Types.string},
            'podrazd_fulltitle': {'path': './СвНаим/@НаимПолн', 'type': Types.string}
        }]
for d in l:
    for key in d:
        print(key)