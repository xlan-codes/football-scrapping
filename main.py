import requests
import json
import socket
import socks

def compatitions():
    link = "http://www.fussball.de/wam_base.json"
    response = requests.get(link)
    response_json = json.loads(response.text)

    link1 = "http://www.fussball.de/wam_arten_{}_{}_{}.json"
    final_link_for_links = "http://www.fussball.de/wam_wettbewerbsurls_{}_{}_{}{}.json"

    for line in response_json['Mandanten']:
        json_file = {
            'area': '',
            'area_name': '',
            'session_id': '',
            'session': '',
            'competitions': []
        }
        line_f = line.strip('_')
        json_file['area'] = line
        json_file['area_name'] = response_json['Mandanten'][line]
        sessions = response_json['Saisons'][line_f]
        for key in sessions:
            key_f = key.strip('_')
            for k in response_json['CompetitionTypes'][line_f][key_f]:
                k_f = k.strip('_')
                f_link = link1.format(line_f, key_f, k_f)
                year = int(key_f)
                if k not in ['_1', '_8', '_7'] or year < 1718:
                    continue
                #second step
                res = requests.get(f_link)
                res_json = json.loads(res.text)
                for l in res_json['Mannschaftsart']:
                    l_f = l.strip('_')
                    if l not in ['_1', '_3', '_4', '_228', '_356', '_359', '_27', '_112', '_174', '_305', '_281', '_331', '_95', '_343', '_9', '_74', '_158', '_212', '_127', '_58', '_241', '_142', '_197', '_41', '_254', '_228']: #herren etc
                        continue;
                    json_file['session'] = l_f
                    json_file['session_id'] = l
                    sessions = res_json['Gebiet'][l_f];
                    for kf in sessions:
                        session_area_name = list(sessions[kf].values())[0]
                        competition_links = []
                        kf_f = '_' + kf.strip('_')
                        flfl = final_link_for_links.format(line_f, key_f, k_f, l)
                        if kf_f not in ['_1', '_3', '_4', '_6', '_52', '_53', '_43', '_145', '_146', '_150', '_153', '_387', '_390', '_392', '_393', '_520', '_714', '_305','_306','_310','_313', '_247','_248','_249','_251','_46','_47','_49','_51','_65','_66','_67','_69','_177','_181','_594','_627', '_256','_257','_262','_263','_129','_130','_132','_135','_584','_114','_116','_119','_597','_31','_32','_36','_207','_210','_213','_214','_626','_232','_233','_235','_702','_815','_268','_273','_282','_283','_284','_286','_595','_77','_78','_84','_158','_159','_162','_165','_221','_222','_711','_713','_292','_294','_299','_300','_361','_93','_94','_96','_99','_190','_191','_195','_198', '_3', '_144','_149','_781','_782','_385','_391','_784','_785','_786','_742','_743','_744','_304','_246','_250','_758','_759','_807','_808','_809','_803','_804','_805','_178','_183','_775','_255','_261','_755','_756','_128','_133','_790','_112','_117','_792','_793','_794','_811','_812','_813','_206','_212','_769','_231','_267','_272','_752','_753','_281','_285','_749','_750','_800','_801','_157','_161','_777','_778','_220','_227','_765','_766','_291','_298','_746','_747','_798','_189','_194','_771','_772', '_92','_97','_76','_83','_45','_50','_64','_68','_27','_30','_35']: # kampjonatet
                            continue;
                        rq = requests.get(flfl)
                        try:
                            rq_json = json.loads(rq.text)
                            competition_categories = rq_json[kf]
                            for category_key in competition_categories:
                                competitions = competition_categories[category_key]
                                for key in competitions:
                                    competition_links.append(
                                        {
                                            'id': key[1:].split('/')[-1],
                                            'name': competitions[key],
                                            "state_name": response_json['Mandanten'][line],
                                            "area_name": session_area_name
                                        }
                                    )
                        except Exception:
                            continue

                        json_file['competitions'].append({
                            'id': '_'+kf,
                            'tier': ''+kf,
                            'name': res_json['Spielklasse'][l_f]['_'+kf],
                            'links': competition_links
                        })


                f = open(json_file['area_name'] + '-' + key_f + '.json', 'w+')
                f.seek(0)
                json.dump(json_file, f, indent=2)
                f.truncate()




if __name__ == '__main__':
    ip = '134.209.96.196'  # change your proxy's ip
    port = 1080  # change your proxy's port
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
    socket.socket = socks.socksocket
    a = requests.get("https://api6.ipify.org?format=json")
    compatitions()
