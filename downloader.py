import os
import queue
import re
import string
import time
from random import choice

import requests

DEBUG = 0
CODE_LENGTH = 7
BASE_URL = "http://zzzpan.com/"
PARAMs = "?/file/view-"
SUFFIX = ".html"
ALPHABETS = string.ascii_uppercase[:] + string.digits
FAIL = 0
VISITED = set()
cnt = 0
SAVE_DIR = "downloaded_files"


def download_file(url, q):
    global FAIL, cnt
    # -------download this url
    html = requests.post(url)

    # if not found such file, add cnt for fail and exit
    if html.status_code != 200:
        FAIL += 1
        if DEBUG:
            print(url, " is invalid, error code: ", html.status_code)
        return
    # set encoding
    html.encoding = "utf-8"

    # find link
    download_link = re.search(r'href="(.+?)" title="本站下载"', html.text)

    # find name and format
    file_prefix = re.search(r'<p>文件名称：(.+?)</p>', html.text)
    file_suffix = re.search(r'<p>文件类型：(.+?)</p>', html.text)
    file_name = file_prefix.group(1) + "." + file_suffix.group(1)
    # if file not exist, download it
    if not os.path.exists(os.getcwd() + '\\' + file_name):
        # print banner
        cnt += 1
        print("\n----------------------------the ", cnt, " th----------------------------")
        print("current url: ", url)

        start = time.clock()
        print(file_name, " is downloading")
        print("file link is ", download_link.group(1))

        # download file
        try:
            downloaded_file = requests.get(download_link.group(1), stream=True)
        except TimeoutError as e:
            print('except:', e)
            return
        except requests.packages.urllib3.exceptions.ProtocolError as e:
            print('except:', e)
            return
        except requests.exceptions.ConnectionError as e:
            print('except:', e)
            return
        end = time.clock()
        print("file downloaded using ", end - start, " seconds")

        # write into local
        start = time.clock()
        print(file_name, "is saving to local")
        with open(file_name, "wb") as file:
            for chunk in downloaded_file.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    file.flush()
                    os.fsync(file.fileno())
        end = time.clock()
        print("file saved using ", end - start, " seconds")
    else:
        print(file_name, " already downloaded\n")

    # add new unvisited urls into q
    urls = re.findall(r'<li><a href="(.+?)">', html.text)
    for url in urls:
        if url not in VISITED:
            q.put(BASE_URL + url)
    print("remaining urls : ", q.qsize())


def generate_next_random_url():
    code = ''
    for i in range(CODE_LENGTH):
        code += choice(ALPHABETS)
    return BASE_URL + PARAMs + code + SUFFIX


def download_file_from_n_random_file(n):
    for i in range(n):
        url = ''
        while True:
            url = generate_next_random_url()
            if url not in VISITED:
                VISITED.add(url)
                break
        download_file(url)


def download_file_by_bfs(initial_urls, max_time):
    global cnt
    if SAVE_DIR not in os.listdir(os.getcwd()):
        os.mkdir(os.getcwd() + "/" + SAVE_DIR)
    os.chdir(os.getcwd() + "/" + SAVE_DIR)
    q = queue.Queue()
    # 加入初始urls
    for url in initial_urls:
        q.put(url)
        # 开始广度优先遍历
    while True:
        url = q.get()
        if url is None:
            break
        VISITED.add(url)
        download_file(url, q)
        if cnt >= max_time:
            return


TOTAL = 100
initial_urls = ["http://zzzpan.com/?/file/view-LN4KUL8.html",
                "http://zzzpan.com/?/file/view-RN4KULE.html",
                "http://zzzpan.com/?/file/view-GN2XMTM.html",
                "http://zzzpan.com/?/file/view-PN2XMTN.html",
                "http://zzzpan.com/?/file/view-ZO0EPKX.html",
                "http://zzzpan.com/?/file/view-CN4KUKR.html",
                "http://zzzpan.com/?/file/view-MNECPC8.html",
                "http://zzzpan.com/?/file/view-HO0IR0Q.html",
                "http://zzzpan.com/?/file/view-HNHJ461.html"
                ]
download_file_by_bfs(initial_urls, TOTAL)
print("-------------------------final result-------------------------");
print("TOTAL: ", TOTAL)
print("FAIL : ", FAIL)
