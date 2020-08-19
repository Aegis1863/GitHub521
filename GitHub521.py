# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:02:56 2020

@author: LiSunBowen
"""
import re
import os
import requests

from collections import Counter

RAW_URL = [
    "github.githubassets.com",
    "camo.githubusercontent.com",
    "github.map.fastly.net",
    "github.global.ssl.fastly.net",
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "user-images.githubusercontent.com",
    "favicons.githubusercontent.com",
    "avatars5.githubusercontent.com",
    "avatars4.githubusercontent.com",
    "avatars3.githubusercontent.com",
    "avatars2.githubusercontent.com",
    "avatars1.githubusercontent.com",
    "avatars0.githubusercontent.com",
    "gist.github.com"]

IPADDRESS_PREFIX = ".ipaddress.com"

HOSTS_TEMPLATE = """# GitHub Host Start
{content}
# GitHub Host End"""

def gethosts(hostsfile):
    #读到原hosts内容
    with open(hostsfile,'r') as fd:
        old_hosts = fd.readlines()
    print('已经读到原hosts文本')
    return old_hosts

def make_ipaddress_url(raw_url: str):
    """
    生成 ipaddress 对应的 url
    :param raw_url: 原始 url
    :return: ipaddress 的 url
    """
    dot_count = raw_url.count(".")
    if dot_count > 1:
        raw_url_list = raw_url.split(".")
        tmp_url = raw_url_list[-2] + "." + raw_url_list[-1]
        ipaddress_url = "https://" + tmp_url + IPADDRESS_PREFIX + "/" + raw_url
    else:
        ipaddress_url = "https://" + raw_url + IPADDRESS_PREFIX
    return ipaddress_url


def get_ip(session: requests.session, raw_url: str):
    url = make_ipaddress_url(raw_url)
    try:
        rs = session.get(url, timeout=15)
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        ip_list = re.findall(pattern, rs.text)
        ip_counter_obj = Counter(ip_list).most_common(1)
        if ip_counter_obj:
            return raw_url, ip_counter_obj[0][0]
        raise Exception("ip address empty")
    except Exception as ex:
        print("get: {}, error: {}".format(url, ex))
        raise Exception

def writehosts(old_hosts, content, hostsfile):
    #删除老hosts中的ip
    for line in range(len(old_hosts)):
        if old_hosts[line] == '# GitHub Host Start\n':
            startline = line
        elif old_hosts[line] == '# GitHub Host End':
            endline = line
    #得到起止行数startline，endline
    for i in range(startline,endline+1)[::-1]:
        del old_hosts[i]
    #在被删除原ip地址的区域增加新的github ip
    old_hosts.append(content)
    #把列表内容全部连接起来
    new_hosts = ''.join(old_hosts)
    #复写入文件
    with open(hostsfile,'w') as fd:
        fd.write(new_hosts)
    print('复写成功')

def flushdns():
    os.system('ipconfig /flushdns')

def main():
    session = requests.session()
    content = ""
    for raw_url in RAW_URL:
        try:
            host_name, ip = get_ip(session, raw_url)
            content += ip.ljust(30) + host_name + "\n"
        except Exception:
            continue
    hosts_content = HOSTS_TEMPLATE.format(content=content)
    hostsfile = "C:\\Windows\\System32\\drivers\\etc\\hosts"
    old_hosts = gethosts(hostsfile)
    writehosts(old_hosts, hosts_content, hostsfile)
    # 刷新DNS缓存
    flushdns()

if __name__ == "__main__":
    main()
