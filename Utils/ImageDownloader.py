import requests
import uuid
import os


class ImageDownloader:
    def __init__(self):
        self.downloaded_images = []

    def download_image(self, pic_url):
        tmp_dir = 'storage/tmp'

        if not(os.path.exists(tmp_dir)):
            os.makedirs(tmp_dir)

        pic_path = f'{tmp_dir}/d_{uuid.uuid4()}'
        with open(pic_path, 'wb') as handle:
            response = requests.get(pic_url, stream=True)

            for block in response.iter_content(1024):
                if not block:
                    handle.close()
                    break

                handle.write(block)

        if response.status_code != 200:
            raise Exception(f'[ImageDownloader] Cannot download image {pic_url}')

        self.downloaded_images.append(pic_path)
        return pic_path

    def cleanup_tmp_dir(self):
        for image in self.downloaded_images:
            try:
                os.remove(path=f"{os.getcwd()}/{image}")
            except:
                pass
