import os
import requests
import time
from datetime import datetime


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
