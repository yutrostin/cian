# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#подгрузим библиотеки
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time

#определим полезную функцию :)
def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))

###НАПИШЕМ И ОБЪЯВИМ ОЧЕНЬ МНОГО ФУНКЦИЙ (ну для меня много :))
#функция чтобы вытащить цену
def getPrice(flat_page):
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return int(price)

#функция чтобы вытащить площадь квартиры
def getSquare(flat_page):
    square = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    square = re.split('<i class="object_descr_details_color"></i>| м<sup>2</sup>', str(square))
    target = re.split(',',str(square[1]))
    target = '.'.join(target)
    return float(target)
    
#функция чтобы вытащить жилую площадь квартиры
#немного коряво вышло, но работает
def getLivesp(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    x = 0
    if space[space.index("Жилая")+2].isdigit()==True:
        if (space[space.index("Жилая")+2].isdigit() & space[space.index("Жилая")+3].isdigit())==True:
            target = [space[space.index("Жилая")+2],space[space.index("Жилая")+3]]
            x = '.'.join(target)
            x = float(x)
        else:
            x = space[space.index("Жилая")+2]
    else:
        x = 'NA'
    return x

#функция чтобы получить площадь кухни
def getKitsp(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    x = 0
    if space[space.index("кухни")+1].isdigit()==True:
        if (space[space.index("кухни")+1].isdigit() & space[space.index("кухни")+2].isdigit())==True:
            target = [space[space.index("кухни")+1],space[space.index("кухни")+2]]
            x = '.'.join(target)
            x = float(x)
        else:
            x = space[space.index("кухни")+1]
    else:
        x = 'NA'
    return x

#функция чтобы получать количество комнат
def getRoom(flat_page):
    rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
    rooms = html_stripper(rooms)
    room_number = ''
    for i in re.split('-|\n', rooms):
        if 'комн' in i:
            break
        else:
            room_number += i
    room_number = "".join(room_number.split())
    return room_number
    
#определим расстояние от центра до квартиры по прямой
    #при этом координаты нулевого километра равны 37.617689 долготы и 55.755822 широты
def getDist(flat_page):
    coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
    coords = re.split('&amp|center=|%2C', str(coords))
    coords_list = []
    for item in coords:
        if item[0].isdigit():
            coords_list.append(item)
    lat = float(coords_list[0])
    lon = float(coords_list[1])
    x1 = 55.755822
    y1=37.617689
    x = ((lat-x1)**2 + (lon-y1)**2)**0.5
    x = x*40000/360
    x = round(x,3)
    return x
    
#зарядим теперь функцию для дистанции до метро
def getMetrdist(flat_page):
    coords = flat_page.find('span', attrs={'class':'object_item_metro_comment'})
    space = re.split('\W+', str(coords))
    if space[space.index('object_item_metro_comment')+1].isdigit()==True:
        x = space[space.index('object_item_metro_comment')+1]
    else:
        x = 'NA'
    return int(x)
    
#пешком или нет до метро? сейчас узнаем
def getWalk(flat_page):
    coords = flat_page.find('span', attrs={'class':'object_item_metro_comment'})
    space = re.split('\W+', str(coords))
    if space[space.index('object_item_metro_comment')+3] == "пешком":
        x = 1
    else:
        x = 0
    return x
    
#определим тип дома
def getBrick(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    if space[space.index('дома')+2]=='кирпично':
        x = 1
    elif space[space.index('дома')+2]=='кирпичный':
        x = 1
    elif space[space.index('дома')+2]=="монолитно":
        x = 1
    elif space[space.index('дома')+2]=="монолитный":
        x = 1
    else:
        x = 0
    return x

#определим есть ли телефон
def getTel(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    if any(x == "Телефон" for x in space)==True:
        if space[space.index('Телефон')+2]=='да':
            x = 1
        else:
            x = 0
    else:
        x = 0
    return x

#определим есть ли балкон
def getBal(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    if space[space.index('Балкон')+1].isdigit() == True:
        x = 1
    else:
        x = 0
    return x

#узнаем этаж квартиры
def getFloor(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    x = space[space.index("Этаж")+1]
    return int(x)

#узнаем количество этажей в доме
def getNFloors(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    x = space[space.index("Этаж")+2]
    return int(x)

#узнаем первичный ли рынок
def getNew(flat_page):
    space = flat_page.findAll('table', attrs={'class':'object_descr_props flat sale'})
    space = html_stripper(space)
    space = re.split('\W+', str(space))
    if space[space.index('дома')+1]=='вторичка':
        x = 0
    else:
        x = 1
    return x

#чуть не забыл про цену
def getPrice(flat_page):
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return int(price)


####ЗАКОНЧИЛИ С ФУНКЦИЯМИ
    
#МОЖНО ЗАПУСКАТЬ
metro = 'http://www.cian.ru/cat.php?deal_type=sale&engine_version=2&metro%5B0%5D={}&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
links = []
s = 0

####159 в рендже выбрано потому что это соответствует количиству станций в ЦИАН
for i in range(1,159):
    for page in range(1, 30):
        page_url =  metro.format(i, page)

        search_page = requests.get(page_url)
        search_page = search_page.content
        search_page = BeautifulSoup(search_page, 'lxml')

        flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
        flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))

        for link in flat_urls:
            if link.isdigit():
                links.append(link)
        s+=1
        print('The page is {}'.format(s))


#объявим датафрейм, куда будем все хранить
flatStats = pd.DataFrame(columns = ['N', 'Rooms', 'Price','Totsp','Livesp',
'Kitsp','Dist','Metrdist','Walk','Brick','Tel','Bal','Floor','Nfloors','New'])

s=0
for i in range(1,len(links)+1):
    try:
        flat_url = 'http://www.cian.ru/sale/flat/' + str(links[i]) + '/'
        flat_page = requests.get(flat_url)
        flat_page = flat_page.content
        flat_page = BeautifulSoup(flat_page, 'lxml')
        to_append = {'N':int(i),'Rooms':getRoom(flat_page),'Price':getPrice(flat_page),'Totsp':getSquare(flat_page),
                     'Livesp':getLivesp(flat_page), 'Kitsp':getKitsp(flat_page), 'Dist':getDist(flat_page),
                     'Metrdist':getMetrdist(flat_page), 'Walk': getWalk(flat_page), 'Brick':getBrick(flat_page),
                     'Tel':getTel(flat_page), 'Bal':getBal(flat_page),'Floor':getFloor(flat_page),
                     'Nfloors':getNFloors(flat_page), 'New':getNew(flat_page)}
        flatStats = flatStats.append(to_append, ignore_index=True)
        print('THE PAGE IS {}'.format(i))
    except:
        print('OOps, something went wrong with the page {}'.format(i))

flatStats.to_csv('C:/Users/Asus/Documents/CMF/flatStats.csv')

######Парсер работал 32 часа и выгрузил 113165 квартир, сделав CSV файл размером 8.5 мегабайт
###я очень доволен, это мой первый парсер, поставьте мне 10 :)