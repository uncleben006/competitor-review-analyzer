"""
    Module for scraping Amazon reviews.
"""

import logging
import time
import os
import json
import requests
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing import List, Generator

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from amazon_review_scraper.conf import amazon_review_scraper_settings
from amazon_review_scraper.models import Product, Review

load_dotenv()
logging.getLogger("WDM").setLevel(logging.ERROR)


class DriverInitializationError(BaseException):
    message = "Unable to initialize Chrome webdriver for scraping."


class DriverGetReviewsError(BaseException):
    message = "Unable to get Amazon review data with Chrome webdriver."


class AmazonReviewScraper:
    """Class for scraping Amazon reviews"""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger if logger else logging.getLogger(__name__)
        # 初始化 Hugging Face 的 Captcha OCR 模型與 processor
        try:
            self._ocr_processor = TrOCRProcessor.from_pretrained("anuashok/ocr-captcha-v3", use_fast=True)
            self._ocr_model = VisionEncoderDecoderModel.from_pretrained("anuashok/ocr-captcha-v3")
            self._logger.info("OCR Captcha 模型載入成功")
        except Exception as e:
            self._logger.exception(f"OCR Captcha 模型載入失敗: {e}")
            self._ocr_processor = None
            self._ocr_model = None

    def _init_chrome_driver(self) -> webdriver.Chrome:
        """Initializes Chrome webdriver"""
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False, # 禁止跳出儲存密碼提示
            "profile.password_manager_enabled": False, # 禁止密碼管理服務
            "profile.default_content_setting_values.notifications": 2 # 禁止通知提示
        })
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver_path = ChromeDriverManager().install()
        if "THIRD_PARTY_NOTICES.chromedriver" in driver_path:
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _login_to_amazon(self, driver: webdriver.Chrome) -> None:
        """
        Logs in to Amazon.
        若檢測到 Amazon 跳出 Captcha 驗證，會透過 OCR 辨識圖片中的文字，並自動填入驗證欄位，再提交表單。
        """
        driver.get("https://www.amazon.com/account/")
        self._handle_captcha(driver)
        time.sleep(1)

        login_email = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "ap_email")))
        login_email.send_keys(os.getenv("AMAZON_EMAIL"))
        continue_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "continue")))
        continue_button.click()
        login_password = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "ap_password")))
        login_password.send_keys(os.getenv("AMAZON_PASSWORD"))        
        sign_in_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "signInSubmit")))
        sign_in_button.click()

        self._handle_captcha(driver)
        time.sleep(1)

    def _handle_captcha(self, driver: webdriver.Chrome) -> None:
        """利用 Hugging Face OCR 模型處理 Captcha 驗證，最多重試 3 次，直到驗證通過 (找到 id 為 ap_email 的輸入欄位)"""
        max_attempts = 3
        for attempt in range(0, max_attempts):
            self._logger.info(f"Captcha 驗證嘗試第 {attempt+1} 次...")
            try:
                captcha_forms = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'form[action="/errors/validateCaptcha"]')))
            except Exception as e:
                self._logger.info("沒有跳出 Captcha 驗證，可以直接登入")
                return
            
            if captcha_forms:
                self._logger.info("檢測到 Captcha 驗證畫面，開始處理...")
                try:
                    # 取得 Captcha 圖片元素與 URL
                    captcha_img = driver.find_element(By.CSS_SELECTOR, 'form[action="/errors/validateCaptcha"] img')
                    captcha_url = captcha_img.get_attribute("src")
                    self._logger.info(f"Captcha 圖片 URL: {captcha_url}")
                    
                    # 下載 Captcha 圖片
                    response = requests.get(captcha_url, stream=True)
                    if response.status_code == 200:
                        image_bytes = BytesIO(response.content)
                        captcha_image = Image.open(image_bytes)
                        
                        # 確保圖片是 RGB 格式
                        captcha_image = captcha_image.convert("RGB")
                        
                        # 使用 Hugging Face OCR 模型進行 Captcha 辨識
                        if self._ocr_processor and self._ocr_model:
                            pixel_values = self._ocr_processor(captcha_image, return_tensors="pt").pixel_values
                            generated_ids = self._ocr_model.generate(pixel_values, num_beams=2, length_penalty=1.3612823161368288)
                            captcha_text = self._ocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                        else:
                            self._logger.error("OCR 模型未正確載入，無法辨識 Captcha")
                            captcha_text = ""
                        
                        self._logger.info(f"OCR 辨識結果: {captcha_text}")
                        
                        # 填入辨識結果
                        captcha_input = driver.find_element(By.ID, "captchacharacters")
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_text)
                        
                        # 提交表單 (點擊 Continue shopping 按鈕)
                        submit_button = driver.find_element(By.CSS_SELECTOR, 'form[action="/errors/validateCaptcha"] button[type="submit"]')
                        submit_button.click()
                        
                        # 等待驗證完成（根據需要調整等待時間）
                        time.sleep(2)
                    else:
                        self._logger.error(f"下載 Captcha 圖片失敗，HTTP 狀態碼: {response.status_code}")
                except Exception as e:
                    self._logger.exception(f"處理 Captcha 過程中發生錯誤: {e}")
            
            # 檢查是否已成功驗證 (檢查是否出現 id 為 ap_email 的元素)
            try:
                login_email = driver.find_element(By.ID, "ap_email")
                if login_email:
                    self._logger.info("Captcha 驗證成功，已進入登入頁面。")
                    break
            except Exception:
                self._logger.info("Captcha 驗證尚未通過，將重試。")
            if attempt == max_attempts:
                self._logger.error("Captcha 驗證重試超過 3 次仍未通過。")
            
    def _logout_from_amazon(self, driver: webdriver.Chrome) -> None:
        """
        Logs out from Amazon
        Always remember to logout after scraping data
        """
        driver.get("https://www.amazon.com")
        account_nav = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "nav-link-accountList")))
        ActionChains(driver).move_to_element(account_nav).perform() # hover to show the sign out button
        sign_out = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "nav-item-signout")))
        sign_out.click()

    def _get_product_info(self, driver: webdriver.Chrome, asin_code: str) -> Product:
        """
        從 Amazon 商品頁面爬取所需資料
        """
        self._logger.info(f"開始爬取 {asin_code} 產品頁資料...")
        try:
            product_name = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, "productTitle"))).text
            product_base_price_block = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".basisPrice")))
            price_str = product_base_price_block.find_element(By.CSS_SELECTOR, ".a-offscreen").get_attribute("innerHTML")
            base_price = float(price_str.replace("$", "").strip())
            price_int = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".priceToPay span.a-price-whole"))).text
            price_decimal = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".priceToPay span.a-price-fraction"))).text
            final_price = float( price_int + "." + price_decimal )
            product_inventory_status = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, "availability"))).text
            self._logger.info(product_name)
            self._logger.info(base_price)
            self._logger.info(final_price)
            self._logger.info(product_inventory_status)
        except Exception as e:
            self._logger.exception(f"爬取 {asin_code} 產品頁資料時發生錯誤: {e}")

        return Product(
            ident_code=asin_code,
            name=product_name,
            base_price=base_price,
            final_price=final_price,
            inventory_status=product_inventory_status
        )
        
    def _get_all_reviews(self, driver: webdriver.Chrome) -> List[Review]:
        """
        從 Amazon 商品評論頁面爬取所有留言（分頁），直到沒有下一頁。
        """
        
        all_reviews = []
        page = 1

        while page <= 2: # only get the first 2 pages
            self._logger.info(f"開始爬取第 {page} 頁評論")

            # 抓取當前頁面的所有 review 區塊
            try:
                review_elements = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "review")))
            except Exception as e:
                self._logger.exception("爬取評論區塊失敗，結束分頁爬取")
                break

            self._logger.info(f"第 {page} 頁找到 {len(review_elements)} 筆評論")
            for review in review_elements:
                try:
                    parsed_review = self._parse_review_data(driver, review)
                    all_reviews.append(parsed_review)
                except Exception:
                    self._logger.exception(f"解析第 {page} 頁評論時發生錯誤")
                    continue

            # 檢查下一頁按鈕是否可點擊（或是否處於 disabled 狀態）
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
                next_button_class = next_button.get_attribute("class")
                if "a-disabled" in next_button_class:
                    self._logger.info("下一頁按鈕被 disable，已到達最後一頁")
                    break
                else:
                    self._logger.info("點擊下一頁按鈕，切換到下一頁")
                    next_button.click()
                    time.sleep(2)  # 等待下一頁載入
                    page += 1
            except Exception as e:
                self._logger.info("找不到下一頁按鈕，結束分頁爬取")
                break

        return all_reviews

    def _parse_review_data(self, driver: webdriver.Chrome, review: WebElement) -> Review:
        """Parses review data from the given review element"""
        author = review.find_element(By.CLASS_NAME, "a-profile-name").text
        content = review.find_element(By.CSS_SELECTOR, "[data-hook='review-body']").text
        title_block = review.find_element(By.CSS_SELECTOR, "[data-hook='review-title']")
        title = title_block.find_elements(By.CSS_SELECTOR, "span")[-1].text.strip()
        rating_text = title_block.find_element(By.CSS_SELECTOR, "i[data-hook='review-star-rating'] span.a-icon-alt").get_attribute("innerHTML")
        rating = float(rating_text.split(" out of ")[0])
        review_date = review.find_element(By.CSS_SELECTOR, "[data-hook='review-date']").text
        self._logger.info(author)
        self._logger.info(content)
        self._logger.info(title)
        self._logger.info(rating_text)
        self._logger.info(rating)
        self._logger.info(review_date)

        try:
            helpful_text = review.find_element(By.CSS_SELECTOR, "[data-hook='helpful-vote-statement']").text
        except Exception:
            helpful_text = "0 people found this helpful"


        try:
            verified_text = review.find_element(By.CSS_SELECTOR, "[data-hook='avp-badge']").text
            verified = verified_text.strip() == "Verified Purchase"
        except Exception:
            verified = False

        return Review(
            author=author,
            content=content,
            rating=rating,
            title=title,
            review_date=review_date,
            verified_purchase=verified,
            helpful_text=helpful_text
        )
    
    def _change_locale_to_new_york(self, driver: webdriver.Chrome) -> None:
        """
        Changes the locale to New York
        Because Amazon shows different reviews and price based on the location
        """
        location_popover = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, 'nav-global-location-popover-link')))
        location_popover.click()
        GLUXZipUpdateInput = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, 'GLUXZipUpdateInput')))
        GLUXZipUpdateInput.send_keys("10001") # New York zip code
        GLUXZipUpdate = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "GLUXZipUpdate")))
        GLUXZipUpdate.click()
        done_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="glowDoneButton"]')))
        done_button.click()
        driver.refresh()

    def _get_product_from_product_page(self, driver: webdriver.Chrome, url: str, asin_code: str) -> Product:
        """Scrapes Amazon product page for product information"""
        driver.get(url)
        time.sleep(1)
        product = self._get_product_info(driver, asin_code)
        return product

    def _get_reviews_from_product_review_page(self, driver: webdriver.Chrome, review_url: str) -> List[Review]:
        """Scrapes Amazon product review page for reviews"""
        driver.get(review_url) # open the product reviews page and get the reviews
        time.sleep(1)
        reviews = self._get_all_reviews(driver)
        return reviews

    def scrape_amazon_products_and_reviews(self, asin_codes: List[str]) -> Generator[List[Review], None, None]:
        """
        Retrieves reviews from Amazon for each given Amazon product ASIN code.
        Yields:
            A list of Review objects for each ASIN code.
        Raises:
            DriverInitializationError: If the Chrome webdriver cannot be initialized.
            DriverGetReviewsError: If scraping reviews fails.
        """
        self._logger.info(f"Scraping Amazon Reviews for product {asin_codes}..")

        try:
            driver = self._init_chrome_driver()
        except Exception as e:
            raise DriverInitializationError from e

        self._login_to_amazon(driver)
        time.sleep(1)
        self._change_locale_to_new_york(driver)
        time.sleep(1)

        for asin_code in asin_codes:
            url = amazon_review_scraper_settings.get_amazon_product_url(asin_code)
            review_url = amazon_review_scraper_settings.get_amazon_product_reviews_url(asin_code)
            try:
                product = self._get_product_from_product_page(driver, url, asin_code)
                reviews_batch = self._get_reviews_from_product_review_page(driver, review_url)
                yield asin_code, product, reviews_batch
            except Exception as e:
                raise DriverGetReviewsError from e
        
        # logout and close the browser
        self._logout_from_amazon(driver)
        driver.close()
