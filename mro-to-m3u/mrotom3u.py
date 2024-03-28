import requests, json, base64, time, random

mroheaders = {
    'authority': 'myradioonline.pl',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://myradioonline.pl',
    'referer': 'https://myradioonline.pl/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'x-requested-with': 'XMLHttpRequest',
}

mrodata = {
    'ord': '1',
    'actP': '1',
    'type': '',
}

radios = {}

actP = 1
while True:
    print(str(actP))
    mrodata['actP'] = actP
    response = requests.post('https://myradioonline.pl/get-radio-list', headers=mroheaders, data=mrodata)
    thing = json.loads(response.content)
    for item in thing["radios"]["list"]:
        name = item["r_name"]
        url = base64.b64decode(item["rsu_url"]).decode('utf-8')
        lang = item["lng"]
        logo = item["settings"]["list_45"].replace("list_45.jpg", "play_250_250.webp")
        if lang not in radios:
            radios[lang] = [[name, url, lang, logo]]
        else:
            radios[lang].append([name, url, lang, logo])
        #radios.append([name, url, lang, logo])
    if thing["moreP"] == False:
        break
    actP = actP + 1
    time.sleep(random.randint(1,5))

print(radios)

for lang in radios:
    with open(lang + ".m3u8", "w", encoding="utf-8") as output:
        output.write("#EXTM3U\n\n")
        for item in radios[lang]:
            output.write("#EXTINF:-1 tvg-logo=\"" + str(item[3]) + "\", " + str(item[0]) + "\n" + str(item[1]) + "\n")