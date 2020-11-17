import hashlib
import io
import os
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException


def __keep_image(folder: str, url: str):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
        return

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder, hashlib.sha1(image_content).hexdigest()[:10] + '.png')
        with open(file_path, 'wb') as f:
            image.save(f, "png")
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def __scroll_to_end(wd, sleep_between_interactions):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(sleep_between_interactions)


def __creat_dir(search_term: str, target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    return target_folder


def google_and_download(search_term: str, driver_path: str, target_path='./images', number_images=5):

    def fetch_img_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: float = 0.8):

        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
        wd.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0

        while image_count < max_links_to_fetch:
            __scroll_to_end(wd, sleep_between_interactions)

            thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)
            print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

            for img in thumbnail_results[results_start:number_results]:
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    print(f"Could not click image {img}.")
                    continue

                actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        image_urls.add(actual_image.get_attribute('src'))

                image_count = len(image_urls)

                if image_count >= max_links_to_fetch:
                    print(f"Found: {image_count} image links, done!")
                    break
            else:
                print("Found:", image_count, "image links, looking for more ...")
                time.sleep(30)
                load_more_button = wd.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")
                return
            results_start = len(thumbnail_results)
        return image_urls

    dest = __creat_dir(search_term, target_path)
    with webdriver.Chrome(executable_path=driver_path) as my_webdriver:
        urls = fetch_img_urls(search_term, number_images, wd=my_webdriver, sleep_between_interactions=1)
        for url in urls:
            __keep_image(dest, url)
        my_webdriver.close()

class Filters:
    URL = "https://stock.adobe.com/pl/search/images?"
    ILLUSTRATIONS = "&filters%5Bcontent_type%3Aillustration%5D=1"
    VECTORS = "&filters%5Bcontent_type%3Azip_vector%5D=1"
    PHOTOS = "?filters%5Bcontent_type%3Aphoto%5D=1"
    SQUARE = "&filters%5Borientation%5D=square"
    VERTICAL = "&filters%5Borientation%5D=vertical"
    HORIZONTAL = "&filters%5Borientation%5D=horizontal"
    QUERY_PREFIX = "load_type=search&native_visual_search=&similar_content_id=&is_recent_search=&search_type=usertyped&k="

    @staticmethod
    def build_query(query: str, style, orientation):
        return Filters.URL + style + orientation + Filters.QUERY_PREFIX + query


def search_and_nothing_but_legal_download(driver_path: str, search_term: str = '', url='', number_images=5,
                                          target_path='./images', style=Filters.ILLUSTRATIONS, orientation=Filters.SQUARE,
                                          folder: str = 'any'):
    def fetch_img_urls(wd: webdriver):
        image_urls = []
        if url == '':
            wd.get(Filters.build_query(search_term, style, orientation))
        else:
            wd.get(url)
        temp = []

        thumbnail_results = wd.find_elements_by_tag_name('img')
        for thumbnail_result in thumbnail_results:
            try:
                temp.append(thumbnail_result.get_attribute('src'))
                if any(extension in thumbnail_result.get_attribute('src') for extension in ('jpg', 'jpeg', 'png')):
                    image_urls.append(thumbnail_result.get_attribute('src'))
            except StaleElementReferenceException:
                print('Reference lost exception')

        return image_urls

    dest = __creat_dir(folder, target_path)
    with webdriver.Chrome(executable_path=driver_path) as my_webdriver:
        urls = fetch_img_urls(my_webdriver)
        for url in urls:
            __keep_image(dest, url)
        my_webdriver.close()


def create_mini_database(driver_path: str):
    sunset_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aillustration%5D=0&filters%5Bcontent_type%3Aphoto%5D=0&k=sunset&order=relevance&safe_search=1&limit=100&search_type=fsc-tile-panel-find-similar&search_page=1&prevk=sunset&acp=&aco=sunset&native_visual_search=&similar_content_id=114283610&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aillustration%5D=0&filters%5Bcontent_type%3Aphoto%5D=0&filters%5Bcontent_type%3A3d%5D=0&filters%5Bcontent_type%3Atemplate%5D=0&filters%5Bcontent_type%3Avideo%5D=0&k=sunset&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=sunset&acp=&aco=sunset&price%5B%24%5D=1&native_visual_search=&similar_content_id=113609379&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aillustration%5D=0&filters%5Bcontent_type%3Aphoto%5D=0&filters%5Bcontent_type%3A3d%5D=0&filters%5Bcontent_type%3Atemplate%5D=0&filters%5Bcontent_type%3Avideo%5D=0&k=sunset&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=sunset&acp=&aco=sunset&price%5B%24%5D=1&native_visual_search=&similar_content_id=121047289&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aillustration%5D=0&filters%5Bcontent_type%3Aphoto%5D=0&filters%5Bcontent_type%3A3d%5D=0&filters%5Bcontent_type%3Atemplate%5D=0&filters%5Bcontent_type%3Avideo%5D=0&k=sunset&order=relevance&safe_search=1&limit=100&search_type=filter-select&search_page=1&prevk=sunset&acp=&aco=sunset&price%5B%24%5D=1&native_visual_search=&similar_content_id=163418564&model_id=&serie_id=&find_similar_by=all&get_facets=1"
    ]

    mountain_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=autosuggest&search_page=1&prevk=landscape&acp=1&aco=mountai&k=mountains&native_visual_search=&similar_content_id=117722469&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=mountains&acp=1&aco=mountai&k=mountains&native_visual_search=&similar_content_id=336030106&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=mountains&acp=1&aco=mountai&k=mountains&native_visual_search=&similar_content_id=299407144&model_id=&serie_id=&find_similar_by=all&get_facets=1"
    ]

    forest_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=horizontal&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=forest&acp=&aco=forest&k=forest&native_visual_search=&similar_content_id=198132838&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=horizontal&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=pagination&search_page=2&prevk=forest&acp=&aco=forest&k=forest&native_visual_search=&similar_content_id=198132838&model_id=&serie_id=&find_similar_by=all&get_facets=0",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=horizontal&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=pagination&search_page=3&prevk=forest&acp=&aco=forest&k=forest&native_visual_search=&similar_content_id=198132838&model_id=&serie_id=&find_similar_by=all&get_facets=0"
    ]

    night_sky_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=sky&acp=&aco=sky&k=sky&native_visual_search=&similar_content_id=111388972&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=pagination&search_page=2&prevk=sky&acp=&aco=sky&k=sky&native_visual_search=&similar_content_id=111388972&model_id=&serie_id=&find_similar_by=all&get_facets=0",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=sky&acp=&aco=sky&k=sky&native_visual_search=&similar_content_id=193075864&model_id=&serie_id=&find_similar_by=all&get_facets=1",
    ]

    simple_cloud_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=visual-search-drag&search_page=1&prevk=cloud&acp=&aco=cloud&k=cloud&native_visual_search=&similar_content_id=153787754&model_id=&serie_id=&find_similar_by=all&get_facets=1",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=pagination&search_page=2&prevk=cloud&acp=&aco=cloud&k=cloud&native_visual_search=&similar_content_id=153787754&model_id=&serie_id=&find_similar_by=all&get_facets=0",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&filters%5Bcontent_type%3Azip_vector%5D=1&order=relevance&safe_search=1&limit=100&search_type=pagination&search_page=3&prevk=cloud&acp=&aco=cloud&k=cloud&native_visual_search=&similar_content_id=153787754&model_id=&serie_id=&find_similar_by=all&get_facets=0"
    ]

    earth_sites = [
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&order=relevance&safe_search=1&search_type=visual-search-drag&limit=100&search_page=1&acp=&k=earth&aco=earth&prevk=earth&native_visual_search=&similar_content_id=259153554&model_id=&serie_id=&find_similar_by=all&get_facets=1"
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&order=relevance&safe_search=1&search_type=pagination&limit=100&search_page=2&acp=&k=earth&aco=earth&prevk=earth&native_visual_search=&similar_content_id=259153554&model_id=&serie_id=&find_similar_by=all&get_facets=0",
        "https://stock.adobe.com/search/images?filters%5Bcontent_type%3Azip_vector%5D=1&filters%5Bcontent_type%3Aimage%5D=1&filters%5Borientation%5D=square&order=relevance&safe_search=1&search_type=pagination&limit=100&search_page=3&acp=&k=earth&aco=earth&prevk=earth&native_visual_search=&similar_content_id=259153554&model_id=&serie_id=&find_similar_by=all&get_facets=0"
    ]

    for sunset_site in sunset_sites:
        search_and_nothing_but_legal_download(driver_path, folder='square_sunsets', url=sunset_site)

    for mountain_site in mountain_sites:
        search_and_nothing_but_legal_download(driver_path, folder='square_mountains', url=mountain_site)

    for forest_site in forest_sites:
        search_and_nothing_but_legal_download(driver_path, folder='horizontal_forests', url=forest_site)

    for night_sky_site in night_sky_sites:
        search_and_nothing_but_legal_download(driver_path, folder='square_night_sky', url=night_sky_site)

    for simple_cloud_site in simple_cloud_sites:
        search_and_nothing_but_legal_download(driver_path, folder='square_simple_cloud', url=simple_cloud_site)

    for earth_site in earth_sites:
        search_and_nothing_but_legal_download(driver_path, folder='square_simple_cloud', url=earth_site)
