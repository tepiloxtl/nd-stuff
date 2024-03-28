import requests, json, base64, time

# Incredubly barebones M3U parser. Might be a bad idea if running on untrusted files lmao. No support for tags and shit, only gets name and link, it's all thats required by navidrome anyway
# Maybe a TODO to expand this, or switch for a lib
def parse_m3u(path):
    stations = {}
    fm3u = open(path, "r", encoding="utf-8").read().splitlines()
    if fm3u[0] != "#EXTM3U":
        print("Not an m3u file??")
        quit()
    for n in range(len(fm3u)):
        if fm3u[n][0:8] == "#EXTINF:":
            stations[fm3u[n].split(",")[1].strip()] = fm3u[n+1]
    return stations

def subsonic_request(method, **kwargs):
    sreq = str(config["subsonic_instance"]["adres"]) + "/rest/" + str(method) + "?u=" + str(config["subsonic_instance"]["login"]) + "&p=" + str(config["subsonic_instance"]["password"]) + "&v=1.16.1&c=testapp&f=json"
    for item in kwargs:
        sreq = sreq + "&" + str(item) + "=" + str(kwargs[item])
    response2 = requests.post(sreq)
    print(response2)
    return response2

# try:
#     txtlista = open('listaaaaa.txt' ,'r+')
#     knownstations = txtlista.read().splitlines()
#     txtlista.close()
# except:
#     txtlista = open('listaaaaa.txt' ,'w+')
#     txtlista.close()
#     knownstations = []

# print(knownstations)

configfile = open("m3utond.json", "r", encoding="utf-8")
config = json.load(configfile)
#print(config)

response2 = subsonic_request(method = "getInternetRadioStations")
nd_radio = json.loads(response2.content)
nd_stations = {}
#print(nd_radio["subsonic-response"]["version"])
#print(nd_radio)

try:
    for item in nd_radio["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
        nd_stations[item["name"]] = [item["id"], item["streamUrl"]]
except:
    pass

print(nd_stations)

for item in config["m3u_files"]:
    m3u_stations = parse_m3u(item["path"])
    #TODO: Deduplication by name?
    #print(m3u_stations)

for station in m3u_stations:
    # if station not in knownstations:
    #     knownstations.append(station)
    if station in nd_stations:
        #updateInternetRadioStation
        pass
    else:
        subsonic_request(method = "createInternetRadioStation", streamUrl = str(m3u_stations[station]), name = str(station))
        #time.sleep(5)

# if config["remove_missing_stations"] == True:
#     for station in knownstations:
#         if station not in m3u_stations:
#             if station in nd_stations:
#                 #deleteInternetRadioStation
#                 pass


    