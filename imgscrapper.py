import hashlib
import io
import os
import time
import requests
from PIL import Image
from selenium import webdriver


def __keep_image(folder: str, url: str):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
        return

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder, hashlib.sha1(image_content).hexdigest()[:10] + '.pdf')
        with open(file_path, 'wb') as f:
            image.save(f, "PDF")
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

    def fetch_img_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: float = 0.3):

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
        urls = fetch_img_urls(search_term, number_images, wd=my_webdriver, sleep_between_interactions=0.3)
        for url in urls:
            __keep_image(dest, url)
        my_webdriver.close()
