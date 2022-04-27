# Задание
# Нужно написать программу, которая будет:
    # Получать фотографии с профиля. Для этого нужно использовать метод photos.get.
    # Сохранять фотографии максимального размера(ширина/высота в пикселях) на Я.Диске.
    # Для имени фотографий использовать количество лайков.
    # Сохранять информацию по фотографиям в json-файл с результатами.

# Обязательные требования к программе:
    # Использовать REST API Я.Диска и ключ, полученный с полигона.
    # Для загруженных фотографий нужно создать свою папку.
    # Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размера (ширина/высота в пикселях) на Я.Диске
    # Сделать прогресс-бар или логирование для отслеживания процесса программы.
    # Код программы должен удовлетворять PEP8.
    # У программы должен быть свой отдельный репозиторий.
    # Все зависимости должны быть указаны в файле requiremеnts.txt.​

from pickle import FALSE, TRUE
from pprint import pprint
import configparser
import os
from xmlrpc.client import boolean
import requests
import datetime
from tqdm import tqdm
import json
import sys


def token_get(type:str) -> str:
    if type == 'vk':
        with open('TOKEN_VK.TXT', 'r') as file:
            return file.read().strip()
    elif type == 'ya':
        with open('TOKEN_YA.TXT', 'r') as file:
            return file.read().strip()
    else:
        return 'TOKEN не задан'

def test():
    print(TOKEN_VK)
    print(TOKEN_YA)

def save_log_file(photos: list, show_phtos = FALSE):
    data = {}
    data['Date'] = str(datetime.datetime.now())
    data['Photos'] = photos
    with open('synchronization_log.txt', 'w') as file_log:
        json.dump(data, file_log)
        print('Файл synchronization_log.txt с информацией о фото записан!')
    if show_phtos == TRUE:
        pprint(photos)

class vk_id:
    def __init__(self, token: str, id: int, ver='5.131'):
        self.token = token
        self.id = id
        self.ver = ver

    def get_profile(self):
        """Метод для тестового получения информации о профайле VK"""
        url = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': self.id, # 'begemot_korovin',
            'access_token': self.token,
            'v': self.ver
        }
        res = requests.get(url, params = params).json()
        return res
   
    def get_photos(self):
        """Метод списка фотографий с сылками"""
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': self.id, # 552934290,#'begemot_korovin',
            'album_id': 'profile',
            'photo_sizes': '1',
            'extended': 1, #возвращаются дополнительные поля
            'access_token': self.token,
            'v': self.ver
        }

        res = requests.get(url, params = params)
        res = res.json()
        # pprint(res)
        # pprint(res.json())
        photos = []
        for photo in res['response']['items']:
            max_size = 0
            url_photo = ''
            for size in photo['sizes']:
                if size['height'] >= max_size:
                    max_size = size['height']
                    url_photo = size['url']
            # date_photo = datetime.datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d %H:%M:%S')
            date_photo = datetime.datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d')
            photos.append({'id': photo['id'], 'likes': photo['likes']['count'], 'url': url_photo, 'date': date_photo})
        return photos

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create_catalog(self, catalog_name: str):
        """Метод создает каталог на яндекс диск"""
        URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}
        params = {"path": catalog_name}
        result = requests.put(f'{URL}', headers=headers, params=params)
        # pprint(result)
        answer = result.status_code
        if answer == 201:
            print(f"Каталог {catalog_name} создан")
        else:
            result = result.json()
            print(f"Ответ {answer}: {result['message']}")

    def upload(self, file_name_full: str, file_name: str, save_path='netology', overwrite=True) -> boolean:
        """Метод загружает файла на яндекс диск"""
        URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}
        params = {"path": f'/{save_path}/{file_name}', "overwrite": overwrite}
        result = requests.get(f'{URL}/upload', headers=headers, params=params).json()
        # pprint(result)
        responce = requests.put(result['href'], data=open(file_name_full, 'rb'))
        responce.raise_for_status()
        if responce.status_code == 201:
            # print(f"Загрузка выполнена {file_name}")
            return TRUE
        else:
            # print(f"Ошибка при загрузке файла! = {responce.status_code}")
            return FALSE


if __name__ == '__main__':
    #  Настройки программы
    config = configparser.ConfigParser()
    config.read("requiremеnts.txt")
    PATH_DOWNLOAD_PHOTOS = config["Настройки программы"]["PATH_DOWNLOAD_PHOTOS"]
    CATALOG_yndex_disk = config["Настройки программы"]["CATALOG_yndex_disk"]
    VK_PROFILE_ID = int(config["Настройки программы"]["VK_PROFILE_ID"])

    TOKEN_VK = config["Настройки программы"]["TOKEN_VK"] # token_get('vk')
    TOKEN_YA = config["Настройки программы"]["TOKEN_YA"] # token_get('ya')

    if TOKEN_YA == '':
        print("Выполнение остановлено - НЕ указан TOREN для доступа к яндекс диску в настройках файла requiremеnts.txt")
        sys.exit()

    # Создаем класс VK и получаем список с фото профайла
    vk_profile = vk_id(TOKEN_VK, VK_PROFILE_ID)
    photos = vk_profile.get_photos()
    # pprint(photos)

    # Создадим объект Яндекс диск 
    uploader = YaUploader(TOKEN_YA)
    uploader.create_catalog(CATALOG_yndex_disk) # созадим каталог для загрузки в него фото
    # # Скачиваем фото и загружаем их на Яндекс диск
    i = 0
    for photo in tqdm(photos):
        # date_photo = datetime.datetime.now().date()
        date_photo = photo['date']
        file_name = f"{photo['likes']}_{photo['id']}_{date_photo}.jpg"
        file_name_full = os.path.join(os.getcwd(), PATH_DOWNLOAD_PHOTOS, file_name)
        result = requests.post(photo['url'])
        with open(file_name_full, 'wb') as file_photo:
            file_photo.write(result.content)
            download = uploader.upload(file_name_full, file_name, CATALOG_yndex_disk)
        # Удаляем файл если он загружен
        if download:
            photos[i]['status'] = 'Загружен'
        else:
            photos[i]['status'] = 'Ошибка'
        os.remove(file_name_full)
        i += 1

    # Сохраним информацию о загруженных фотографиях в log файл
    save_log_file(photos)

