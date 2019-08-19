import requests
import hashlib
import json
import tqdm
import os
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def get_major_list(index):
    ua = UserAgent()
    url = 'https://w5.ab.ust.hk/wcq/cgi-bin/' + str(index) + '/'
    url_sub = url + 'subject/'
    headers = {'User-Agent': ua.random}
    r = requests.get(url, headers=headers)
    reg = '/wcq/cgi-bin/' + str(index) + '/subject/([A-Z]+)'
    ret = re.findall(reg, r.text)
    res = []
    for x in ret:
        res.append((x, url_sub + x))
    res = list(set(res))
    res.sort()
    return res

def crawl(index, generate_md5 = True):
    major_list = get_major_list(index)
    result = dict()
    md5_result = dict()
    with tqdm.tqdm(total = len(major_list)) as bar:
        for maj in major_list:
            txt = requests.get(maj[1]).text
            soup = BeautifulSoup(txt, 'html.parser')
            title = soup.find_all('h2')
            content = soup.find_all('table', {'class' : 'sections'})
            for i in range(len(title)):
                reg = '([A-Z0-9 ]+) - ([\s\S]+) \(([0-9])'
                re_ret = re.match(reg, title[i].get_text())
                course_code = re_ret[1].replace(' ', '')
                course_name = re_ret[2]
                course_credit = re_ret[3]
                course_slots = []
                ret = content[i].find_all('tr', {'class' : ['newsect secteven', 'newsect sectodd', 'secteven', 'sectodd']})
                section = None
                quota = None
                avail = None
                enrol = None
                wait = None
                time = []
                venue = []
                ins = []
                for j in range(len(ret)):
                    tt = ret[j].find_all('td')
                    if 'newsect' in ret[j].attrs['class']:
                        if j > 0:
                            course_slots.append({
                                'section' : section,
                                'time' : time,
                                'venue' : venue,
                                'instructor' : ins,
                                'quota' : quota,
                                'enrol' : enrol,
                                'avail' : avail,
                                'wait' : wait
                                })
                        time = []
                        venue = []
                        ins = []
                        section = tt[0].get_text('\n', '<br>')
                        time.append(tt[1].get_text('\n', '<br>'))
                        venue.append(tt[2].get_text('\n', '<br>'))
                        ins.append(tt[3].get_text('\n', '<br>'))
                        quota = tt[4].get_text('\n', '<br>')
                        enrol = tt[5].get_text('\n', '<br>')
                        avail = tt[6].get_text('\n', '<br>')
                        wait = tt[7].get_text('\n', '<br>')
                    else:
                        time.append(tt[0].get_text('\n', '<br>'))
                        venue.append(tt[1].get_text('\n', '<br>'))
                        ins.append(tt[2].get_text('\n', '<br>'))
                    if j == len(ret) - 1:
                        course_slots.append({
                            'section' : section,
                            'time' : time,
                            'venue' : venue,
                            'instructor' : ins,
                            'quota' : quota,
                            'enrol' : enrol,
                            'avail' : avail,
                            'wait' : wait
                            })
                result[course_code] = {
                    'course_code' : course_code,
                    'course_name' : course_name,
                    'course_credit' : course_credit,
                    'course_slots' : course_slots
                }
                if generate_md5:
                    md5_result[course_code] = hashlib.md5(json.dumps(result[course_code], sort_keys = True).encode('utf-8')).hexdigest()
            bar.update(1)
    return [result, md5_result]