import os
import requests
import time
from datetime import datetime
from urllib.parse import urlparse, urlunparse, urljoin


def timestamp():
    # Converting datetime object to string
    dateTimeObj = datetime.now()

    timestampStr = dateTimeObj.strftime("%Y_%m_%d_%H_%M_%S_%f")
    return timestampStr


def dl_image(url, basename, root, overwrite=False):
    """
    Given the `url`, we will download the file. The file will be saved at the `root` directory, the file name will be the `basename` + the `url`'s extension.
    """
    if not os.path.exists(root):
        os.makedirs(root)
    ext = os.path.splitext(url)[1]
    filename = basename + ext
    filepath = f'{root}/{filename}'

    if os.path.exists(filepath) and not overwrite:
        return

    try:
        with open(filepath, 'wb') as handle:
            res = requests.get(url, stream=True)
            if not res.status_code == 200:
                print(res)
                # TODO remove `filepath`
                return

            for block in res.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    except:
        os.remove(filepath)


def get_episode_url(url):
    # ref ['https', 'web-ace.jp', '/youngaceup/contents/1000117/episode', '', '', '']
    url_parts = list(urlparse(url))
    path = url_parts[2]

    path_components = path.split('/')
    path_components = list(filter(len, path_components))

    if len(path_components) < 3:
        print(f'{url} does not have enough information to retrieve a specific manga.')
        return

    path_components = path_components[:3]
    path_components.append('episode')
    path = '/'.join(path_components)

    url_parts[2] = path

    return urlunparse(url_parts)
