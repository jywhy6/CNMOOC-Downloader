from requests_html import HTMLSession
import requests
import re
import os
import time
import sys
import random

# Get it from navigation page URL
mooc_num = 1145141919810

# Configurations
# Whatever you choose, it will give you all the direct download links
download_pdf = True
download_mp4 = False

# Cookies needed can be found in request headers
# Use Chrome -> F12 -> Network -> Request Headers
cookie_file = open("cookie", "r")
tmp_cookies = cookie_file.read().strip().split("; ")
cookie_file.close()
cookies = {}
for tmp_cookie in tmp_cookies:
    cookies[tmp_cookie.split("=")[0]] = tmp_cookie.split("=")[1]
# print(cookies)

headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

session = HTMLSession()

url_get_navigation = "https://cnmooc.org/portal/session/unitNavigation/" + str(mooc_num) + ".mooc"
navigation_page = session.get(
    url_get_navigation, cookies=cookies, headers=headers)
count = 0
flag = False
while navigation_page.status_code != 200:
    time.sleep(random.randint(5, 10))
    navigation_page = requests.get(url_get_navigation, cookies=cookies, headers=headers)
    count = count + 1
    if (count > 5):
        flag = True
        break
if (flag):
    print("Failed: Course " + str(mooc_num))
    exit(1)

course_name = navigation_page.html.find("h3.model-title.substr", first = True).text
print("Course Name: " + course_name)
teacher_name = navigation_page.html.find(
    "span.model-tname.substr", first=True).text
print("Teacher Name: " + teacher_name)

folder_name = teacher_name + " - " + course_name
folder_name = re.sub(r'[\/:*?"<>|]', '-', folder_name)

if not os.path.exists(str(folder_name)):
    os.makedirs(str(folder_name))

lecture_elements = navigation_page.html.find(
    "a.lecture-action", first=False)

pdf_item_metadata = []
mp4_item_metadata = []
pdf_download_urls = []
mp4_download_urls = []
for element in lecture_elements:
    if (element.find("i.icon-play01")):
        mp4_item_metadata.append({
            "itemid": element.attrs["itemid"],
            "title": element.attrs["title"]
        })
        # print(element.attrs["title"])
    elif (element.find("i.icon-play01-done")):
        mp4_item_metadata.append({
            "itemid": element.attrs["itemid"],
            "title": element.attrs["title"]
        })
    elif (element.find("i.icon-doc")):
        pdf_item_metadata.append({
            "itemid": element.attrs["itemid"],
            "title": element.attrs["title"]
        })
        # print(element.attrs["title"])
    elif (element.find("i.icon-doc-done")):
        pdf_item_metadata.append({
            "itemid": element.attrs["itemid"],
            "title": element.attrs["title"]
        })
    else:
        print("Ignored: " + element.attrs["itemid"] + ", " + element.attrs["title"])

subcount = 1
for item in pdf_item_metadata:
    # pdf: itemType = 20, mp4: itemType = 10
    url_get_item = "https://cnmooc.org/study/play.mooc?itemId=" + item[
        "itemid"] + "&itemType=20&testPaperId="
    item_page_req = requests.post(url_get_item, cookies=cookies, headers=headers)
    count = 0
    flag = False
    while item_page_req.status_code != 200:
        time.sleep(random.randint(5, 10))
        item_page_req = requests.get(
            url_get_item, cookies=cookies, headers=headers)
        count = count + 1
        if (count > 5):
            flag = True
            break
    if (flag):
        print("Failed: " + item["itemid"] + ", " + item["title"])
        subcount = subcount + 1
        continue
    else:
        item_page_html = str(item_page_req.content, encoding='utf-8')
        url_get_file = "https://cnmooc.org" + item_page_html[
            item_page_html.find("/repo"):item_page_html.find(".pdf") + 4]
        # open("test_pdf.html", "w").write(item_page_html)
        print(url_get_file)
        if(url_get_file):
            pdf_download_urls.append(url_get_file)
            if(download_pdf):
                pdf_data_req = requests.get(
                    url_get_file, cookies=cookies, headers=headers)
                count = 0
                flag = False
                while pdf_data_req.status_code != 200:
                    time.sleep(random.randint(5, 10))
                    pdf_data_req = requests.get(url_get_file, cookies=cookies, headers=headers)
                    count = count + 1
                    if (count > 5):
                        flag = True
                        break
                if (flag):
                    print("Failed: " + item["itemid"] + ", " + item["title"])
                    subcount = subcount + 1
                    continue
                print("Success: " + item["itemid"] + ", " + item["title"])
                pdf_data = pdf_data_req.content
                open(
                    folder_name + "\\" + str(subcount) + "." +
                    item["title"].strip(".pdf") + ".pdf", "wb").write(pdf_data)
                subcount = subcount + 1

subcount = 1
for item in mp4_item_metadata:
    # pdf: itemType = 20, mp4: itemType = 10
    url_get_item = "https://cnmooc.org/study/play.mooc?itemId=" + item[
        "itemid"] + "&itemType=10&testPaperId="
    item_page_req = requests.post(
        url_get_item, cookies=cookies, headers=headers)
    count = 0
    flag = False
    while item_page_req.status_code != 200:
        time.sleep(random.randint(5, 10))
        item_page_req = requests.get(
            url_get_item, cookies=cookies, headers=headers)
        count = count + 1
        if (count > 5):
            flag = True
            break
    if (flag):
        print("Failed: " + item["itemid"] + ", " + item["title"])
        subcount = subcount + 1
        continue
    else:
        item_page_html = str(item_page_req.content, encoding='utf-8')
        # Tricky
        url_get_file = item_page_html[
            item_page_html.find("https://s.cnmooc.org"):item_page_html.
            find(".jpg")] + ".mp4"
        print(url_get_file)
        if (url_get_file):
            mp4_download_urls.append(url_get_file)
            if(download_mp4):
                mp4_data_req = requests.get(
                    url_get_file, cookies=cookies, headers=headers)
                count = 0
                flag = False
                while mp4_data_req.status_code != 200:
                    time.sleep(random.randint(5, 10))
                    mp4_data_req = requests.get(url_get_file, cookies=cookies, headers=headers)
                    count = count + 1
                    if (count > 5):
                        flag = True
                        break
                if (flag):
                    print("Failed: " + item["itemid"] + ", " + item["title"])
                    subcount = subcount + 1
                    continue
                print("Success: " + item["itemid"] + ", " + item["title"])
                mp4_data = mp4_data_req.content
                open(folder_name + "\\" + str(subcount) + "." + item["title"].strip(".mp4") + ".mp4","wb").write(mp4_data)
                subcount = subcount + 1

pdf_download_urls_file = open(folder_name + "\\" + "download.txt", "a")
for url in pdf_download_urls:
    pdf_download_urls_file.write(url + '\n')

mp4_download_urls_file = open(folder_name + "\\" + "download.txt", "a")
for url in mp4_download_urls:
    mp4_download_urls_file.write(url + '\n')
