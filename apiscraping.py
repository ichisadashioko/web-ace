#!/usr/bin/env python3
# encoding=utf-8
import time
import re
import os
import json
from urllib.parse import urlparse, urlunparse, urljoin

# external modules
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

# local modules
from config import dl_root
from utils import dl_image, timestamp, get_episode_url


def parse_manga_page(source: str, page_url: str):
    soup = BeautifulSoup(source)

    # get the manga title
    title = None
    title_divs = soup.select('#breadcrumb li')

    if len(title_divs) >= 3:
        title_div = title_divs[2]
        title = title_div.text

    if title is None:
        # fallback to timestamp
        title = timestamp()

    # get the list of chapters
    anchor_list = soup.find('ul', attrs={'class': 'table-view'}).find_all('a')
    chapters = [{
        'title': a.find('p', attrs={'class': 'text-bold'}).text,
        'url': urljoin(page_url, a.attrs['href']),
    } for a in anchor_list if a.find('p', attrs={'class': 'text-bold'}) is not None]

    # reverse chapters order
    chapters.reverse()

    return {
        'title': title,
        'chapters': chapters,
    }


def get_images(url):
    """
    Sample url: https://web-ace.jp/youngaceup/contents/1000117/episode/3711/
    """

    json_url = urljoin(url, 'json')
    res = requests.get(json_url)
    if not res.status_code == 200:
        return

    img_urls = res.json()
    return img_urls


def dl_manga(url):
    """
    Sample url: https://web-ace.jp/youngaceup/contents/1000117/episode/
    """
    episode_url = get_episode_url(url)

    if episode_url is None:
        return

    res = requests.get(episode_url)
    if not res.ok:
        print(res)
        return

    # sometimes we put old URL, it will be redirected to the main manga page
    if res.is_redirect:
        return dl_manga(res.url)

    manga = parse_manga_page(res.text, res.url)
    chapters = manga['chapters']
    title = manga['title']

    print(f'Detected manga {title}.')
    print(f'Starting to retrieve information about {len(chapters)} chapter(s).')  # noqa

    pbar = tqdm(chapters)
    for chapter in pbar:
        _url = chapter['url']
        pbar.set_description(_url)

        images = get_images(_url)
        images = list(map(lambda x: urljoin(_url, x), images))
        chapter['images'] = images

    return manga


def create_download_jobs(manga):
    dl_jobs = []

    title = manga['title']
    chapters = manga['chapters']
    for chapter in chapters:
        chapter_title = chapter['title']
        chapter_dl_dir = f'{dl_root}/{title}/{chapter_title}'
        images = chapter['images']
        for i in range(len(images)):
            job = {
                'url': images[i],
                'basename': str(i).zfill(3),
                'path': chapter_dl_dir,
            }

            dl_jobs.append(job)

    return dl_jobs


if __name__ == '__main__':
    manga_urls = [
        'https://web-ace.jp/tmca/contents/2000015/episode/',  # Fate/Grand Order -Epic of Remnant- 亜種特異点EX 深海電脳楽土 SE.RA.PH # noqa
        'https://web-ace.jp/youngaceup/contents/1000064/episode/',  # パシリな僕と恋する番長さん
        'https://web-ace.jp/youngaceup/contents/1000117/episode/',  # 世界最高の暗殺者、異世界貴族に転生する
        'https://web-ace.jp/youngaceup/contents/1000091/episode/',  # 勇者、辞めます
        'https://web-ace.jp/youngaceup/contents/1000021/episode/',  # 奪う者 奪われる者
        'https://web-ace.jp/youngaceup/contents/1000080/episode/',  # 平凡なる皇帝
        'https://web-ace.jp/youngaceup/contents/1000046/episode/',  # 異世界建国記
        'https://web-ace.jp/youngaceup/contents/1000125/episode/',  # 針子の乙女
        'https://web-ace.jp/youngaceup/contents/1000049/episode/',  # 回復術士のやり直し
        'https://web-ace.jp/youngaceup/contents/1000133/',  # マジカル☆エクスプローラー エロゲの友人キャラに転生したけど、ゲーム知識使って自由に生きる # noqa
        'https://web-ace.jp/youngaceup/contents/1000136/',  # 三大陸英雄記
        'https://web-ace.jp/youngaceup/contents/1000126/',  # ゼロスキルの料理番
        'https://web-ace.jp/youngaceup/contents/1000015/episode/',  # 賢者の孫
        'https://web-ace.jp/youngaceup/contents/1000124/episode/',  # 帰ってください！ 阿久津さん
        'https://web-ace.jp/youngaceup/contents/1000129/',  # 賢者の孫SS
        'https://web-ace.jp/youngaceup/contents/1000122/',  # 賢者の孫SP
        'https://web-ace.jp/youngaceup/contents/1000105/',  # 賢者の孫 Extra Story
        'https://web-ace.jp/youngaceup/contents/1000136/',  # 三大陸英雄記
    ]

    for manga_url in manga_urls:
        print(f'Retrieving information about {manga_url}')
        manga = dl_manga(manga_url)

        if manga is None:
            print(f'Failed to load {manga_url}')
            continue

        title = manga['title']
        print(f'Starting to download {title}')
        dl_jobs = create_download_jobs(manga)

        for job in tqdm(dl_jobs):
            url = job['url']
            basename = job['basename']
            dl_path = job['path']

            dl_image(url, basename, dl_path)
