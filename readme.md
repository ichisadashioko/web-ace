# Scraping `web-ace.jp` website

Everything here is subjected to changes anytime.

## Method 1: Using selenium

`web-ace` does not store image URLs inside the html source page (`img` tag's `src` attribute) to prevent excessive traffic usage. However, they also do not store them in the alternative `data-src` attribute. The images are loaded dynamically as user scrolling down with some `Javascript`.

The notebook [`scape_with_selenium`](./scrape_with_selenium.ipynb) demonstrates automating human action for scrolling. After that, we traverse through the modified html source page to retreive the image URLs.

__Note__

- You will need [`chromedriver`](https://chromedriver.chromium.org) on your `PATH`.
- As we only retreive image URLs, there is somethings we can to do improve page loading speed. However, you should change some of the `time.sleep()` duration to suite your internet speed and CPU limit for execution of Javascript logic of `web-ace`.

    - Disable image loading and other settings via Chrome's `Site settings` (remember to exclude Javascript)

## Method 2: `JSON` endpoint

I discover this endpoint after using and extension called [`Save All Resources`](https://chrome.google.com/webstore/detail/save-all-resources/abpdnfjocnmdomablahdcfnoggeeiedb). I searched for the retreived image URL in all the resources and discovered that they are all in an request.

For example:

- Chapter URL: `https://web-ace.jp/youngaceup/contents/1000117/episode/4060/`
- Image URLs endpoint: `https://web-ace.jp/youngaceup/contents/1000117/episode/4060/json`

They added another endpoint for storing all the image URLs. I think this is pretty neat because I don't have to scrape the html source page anymore. The response is returned as shown below.

```json
[
    "/img/youngaceup/contents/1000117/comic/YAUP_incredible_assassin_006_1_001_cmp-79ebd1d1-4a41-4cf6-baa3-83dc83c2e657.jpg",
    "/img/youngaceup/contents/1000117/comic/YAUP_incredible_assassin_999_AD_cmp-494d4817-5c38-47c5-a2da-aa7b5788cb92.jpg"
]
```

The code for using this method in the [`json-method.py`](./json-method.py) script.

# URL structure

| example | description |
|---------|-------------|
| `https://web-ace.jp` | The website base URL |
| `https://web-ace.jp/youngaceup/contents/1000117` | The manga with ID `1000117` main page |
| `https://web-ace.jp/youngaceup/contents/1000117/episode` | List all the manga chapters |
| `https://web-ace.jp/youngaceup/contents/1000117/episode/4060` | The chapter URL with ID `4060` |
| `https://web-ace.jp/youngaceup/contents/1000117/episode/4060/json` | List of all image URLs in chapter |

# Change log

## 2020-02-22

- Manga title's class name is not consistent.