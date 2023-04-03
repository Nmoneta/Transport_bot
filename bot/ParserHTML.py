import requests
from bs4 import BeautifulSoup
import json
import re

url="https://igis-transport.ru/izh/"
#
headers = {
    "Accept": "*/*",
}
def get_tranport_type():
    req = requests.get(url,headers=headers)
    src = req.text
    soup = BeautifulSoup(src,"lxml")
    all_transport_hrefs = soup.find(class_="col-6-m").find(class_="city").find_all(class_="full")
    transport_categories_dict = {}
    for item in all_transport_hrefs:
        #print(item.find(class_="transport-label"))
        if(item.find(class_="transport-label") != None):
            transport_name = item.find(class_="transport-label").get_text().replace('\n','',2).strip()
            transport_href = "https://m.igis-transport.ru" + item.get("href")
            transport_categories_dict[transport_name] = transport_href
    with open("all_categories_dict.json", "w") as file:
        json.dump(transport_categories_dict, file,indent=2)


def get_transport_num():
    with open("all_categories_dict.json","r") as file:
        all_categories = json.load(file)
    for category_name, category_href in all_categories.items():
        req=requests.get(url=category_href,headers=headers)
        src=req.text
        soup = BeautifulSoup(src,"lxml")
        data_num = []
        numbers_href = soup.find(class_="numbers").find_all('a')
        with open(f"data/{category_name}.json", "w") as file:
            json.dump({},file,indent=2)
        with open(f"data/{category_name}.json", "r") as file:
            data_num = json.load(file)
            data = {}
        for href in numbers_href:
            forward_href = "https://m.igis-transport.ru" + href['href']+'?'
            back_href =forward_href.replace('forward','back')
            data[f'{href.text.strip()}'] = [
                forward_href,
                back_href
            ]

            if(href.text.strip() == '79'):
                break
        data_num["response"] = data
        with open(f"data/{category_name}.json", "w") as file:
            json.dump(data_num,file,indent=2)
get_transport_num()
def parse(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    return soup

def forward(url):
    position = []
    soup = parse(url)
    row = soup.find_all(class_='row')
    i = 0
    with open('forward.html','w',encoding='UTF-8') as file:
        file.write(str(soup))
    for stops in row:

        if(stops.find(class_ = 'name').find('a')):#work
            if(stops.find(class_ = 'position').find('a')):
                text = str(stops.find('div', title=True)['title']) + '\n'
                match = re.search('(Едет .+?)\n', text).group(1)
                if (stops.find(class_="citybus-down-lowfloor-park") or stops.find(class_="citybus-stop-lowfloor-park")):
                    park = True
                else: park = False
                position.append({
                    "Position":"Stops",
                    "Stops":str(stops.find(class_ = "name").text).strip(),
                    "Orient": "forward",
                    "EndStops":str(match),
                    "Park":park
                    })
        else:
            if (stops.find(class_='position').find('a')):
                text = str(stops.find('div', title=True)['title']) + '\n'
                match = re.search('(Едет .+?)\n', text).group(1)
                if (stops.find(class_="citybus-down-lowfloor-park") or stops.find(class_="citybus-stop-lowfloor-park")):
                    park = True
                else: park = False
                position.append({"Position": "Between_Stops",
                    "Stops" : str(row[i-1].find(class_ = "name").text).strip(),
                    "Orient": "forward",
                    "EndStops" : str(match),
                    "Park":park
                    })
        i+=1
    return position

def back(url):
    position = []
    soup = parse(url)
    row = soup.find_all(class_='row')
    i = 0
    with open('forward.html','w',encoding='UTF-8') as file:
        file.write(str(soup))
    for stops in row:
        if(stops.find(class_='name').find('a')):#work
            if(stops.find(class_='position').find('a')):
                text = str(stops.find('div', title=True)['title']) + '\n'
                match = re.search('(Едет .+?)\n', text).group(1)
                if (stops.find(class_="citybus-down-lowfloor-park") or stops.find(class_="citybus-stop-lowfloor-park")):
                    park = True
                else: park = False
                # park = True
                position.append({
                    "Position": "Stops",
                    "Stops": str(stops.find(class_ = "name").text).strip(),
                    "Orient": "back",
                    "EndStops": str(match),
                    "Park":park
                    })
        else:
            if (stops.find(class_='position').find('a')):
                text = str(stops.find('div', title=True)['title']) + '\n'
                match = re.search('(Едет .+?)\n', text).group(1)
                if (stops.find(class_="citybus-down-lowfloor-park") or stops.find(class_="citybus-stop-lowfloor-park")):
                    park = True
                else: park = False
                # park = True
                position.append({"Position": "Between_Stops",
                    "Stops": str(row[i-1].find(class_="name").text).strip(),
                    "Orient": "back",
                    "EndStops": str(match),
                    "Park":park
                    })
        i+=1
    return position


def position(tranport_num,type_transport):
    with open(f"data/{type_transport}.json", "r") as file:
        all_categories = json.load(file)
    for item in all_categories['response']:
        num = item
        if(num.strip() == tranport_num.strip()):
            hrefs = all_categories['response'][num]
            dict_row = []
            for href in hrefs:
                if('forward' in href):
                   pos_forward = forward(href)
                if('back' in href):
                   pos_back = back(href)
            for i in pos_forward:
                dict_row.append(i)
            for i in pos_back:
                dict_row.append(i)
            with open(f"position.json","w") as file:
                json.dump(dict_row,file,indent=2)

# get_transport_num()
