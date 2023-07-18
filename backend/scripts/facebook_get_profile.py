from core.webdriver import Webdriver


class Client(Webdriver):
    def __init__(self):
        super().__init__()
        from undetected_chromedriver import Chrome
        from nb_log import get_logger

        self.driver: Chrome = None
        self.logger = get_logger()

    def start(self):
        """Start"""
        import time
        import re
        import requests
        import base64
        from urllib.parse import unquote
        url = 'https://fb.com/me'
        if url not in self.driver.current_url:
            self.driver.get(url)
        try:
            self.logger.info("已進入個人資料頁")
            time.sleep(0.5)
            re_pattern = r'"profilePicLarge":{"uri":"(.+)"},"profilePicMedium"'
            match_guides = re.findall(re_pattern, self.driver.page_source)
            img_url = unquote(match_guides[0].replace("\\/", "/"))
            # 取得圖片的二進位資料
            response = requests.get(img_url)
            image_data = response.content

            # 將圖片轉換成 Base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            re_pattern = r'"USER_ID":"(.+?)","NAME":"(.+?)"'
            match_guides = re.findall(re_pattern, self.driver.page_source)
            user_id = match_guides[0][0]
            name = bytes(match_guides[0][1], 'utf-8').decode('unicode_escape')
            self.config['facebook']['user_id'] = user_id
            self.config['facebook']['name'] = name
            self.config['facebook']['img'] = base64_image

            self.save_config()
            self.driver_quit()
        except TimeoutError:
            if "目前無法提供此內容" in self.driver.page_source:
                self.logger.error('目前無法提供此內容')
            elif "無影片可顯示" in self.driver.page_source:
                self.logger.error('無影片可顯示，可能關播了')
            self.driver_quit()
        except Exception as e:
            self.logger.exception(e)
            self.driver_quit()
        """End"""
