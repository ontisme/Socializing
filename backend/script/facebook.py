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
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver import Keys
        params = {"params_text_here"}
        # 選單
        fb_menu_button_comment = "//span[text()='留言']"
        fb_menu_button_like = "//span[text()='讚']"
        fb_menu_button_share = "//span[text()='分享']"
        fb_comment_box = "//div[text()='留言……'][last()]/preceding-sibling::div/p"
        fb_share_box = "//*[contains(text(),'立即分享')]"
        url = f'https://www.facebook.com/{params["page_id"]}/videos/?ref=page_internal'

        try:
            if url not in self.driver.current_url:
                self.driver.get(url)
            # 等待 "留言" 元素出現
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, fb_menu_button_comment)))
            action = params["action"].lower()
            self.logger.info("已進入直播間")
            if action != "like":
                self.logger.info("點擊留言框")
                time.sleep(0.5)
                self.driver.find_element(By.XPATH, fb_menu_button_comment).click()
                self.logger.info("等待出現留言框")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, fb_comment_box)))

            if action == "like":
                self.logger.info("點擊按讚")
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, fb_menu_button_like)))
                elements = self.driver.find_elements(By.XPATH, fb_menu_button_like)
                for i in elements:
                    if i.is_displayed():
                        i.click()
                self.logger.info("成功按讚")
            elif action == "share":
                self.logger.info("點擊分享鈕")
                self.driver.find_element(By.XPATH, fb_menu_button_share).click()
                self.logger.info("等待分享框出現")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, fb_share_box)))
                self.driver.find_element(By.XPATH, fb_share_box).click()
                self.logger.info("成功分享")
            elif action == "comment":
                self.logger.info("正在留言")
                element = self.driver.find_element(By.XPATH, fb_comment_box)
                element.click()
                element.send_keys(params['comment'])
                element.send_keys(Keys.ENTER)
                self.logger.info("成功留言")

        except TimeoutError:
            if "目前無法提供此內容" in self.driver.page_source:
                self.logger.error('目前無法提供此內容')
            elif "無影片可顯示" in self.driver.page_source:
                self.logger.error('無影片可顯示，可能關播了')

        # 休息時間
        self.logger.info(f'休息 {params["idle_time"]} 秒')
        current_time = 0
        # 如果有其他排程馬上退出
        while current_time < params['idle_time']:
            time.sleep(1)
            if len(self.task_queue_list) > 0:
                self.logger.info('檢測到其餘排程，強制結束休息')
                break
            current_time += 1

        if current_time >= params['idle_time']:
            self.logger.info('休息時間到，關閉裝置')
            self.driver_quit()
        """End"""
