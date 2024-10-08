import asyncio
import concurrent.futures as pool
import csv
import logging
import time
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")
LAPTOP_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/laptops")
TABLETS_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/tablets")
TOUCH_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/phones/touch")
COMPUTER_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers")
PHONE_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/phones")


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


PRODUCT_FIELDS = [field.name for field in fields(Product)]


def get_single_laptop(laptop: BeautifulSoup) -> Product:
    return Product(
        title=laptop.select_one("a.title")["title"],
        description=laptop.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(laptop.select_one("h4.price").text.replace("$", "")),
        rating=len(laptop.select("span.ws-icon")),
        num_of_reviews=int(laptop.select_one("p.review-count").text.split()[0])
    )


def get_single_tablet(tablet: BeautifulSoup) -> Product:
    return Product(
        title=tablet.select_one("a.title")["title"],
        description=tablet.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(tablet.select_one("h4.price").text.replace("$", "")),
        rating=len(tablet.select("span.ws-icon")),
        num_of_reviews=int(tablet.select_one("p.review-count").text.split()[0])
    )


def get_single_touch(touch: BeautifulSoup) -> Product:
    return Product(
        title=touch.select_one("a.title")["title"],
        description=touch.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(touch.select_one("h4.price").text.replace("$", "")),
        rating=len(touch.select("span.ws-icon")),
        num_of_reviews=int(touch.select_one("p.review-count").text.split()[0])
    )


async def get_single_phone(phone: BeautifulSoup) -> Product:
    return Product(
        title=phone.select_one("a.title")["title"],
        description=phone.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(phone.select_one("h4.price").text.replace("$", "")),
        rating=len(phone.select("span.ws-icon")),
        num_of_reviews=int(phone.select_one("p.review-count").text.split()[0])
    )


async def parse_single_home_product(product: BeautifulSoup) -> Product:
    return Product(
        title=product.select_one("a.title")["title"],
        description=product.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(product.select_one("h4.price").text.replace("$", "")),
        rating=len(product.select("span.ws-icon")),
        num_of_reviews=int(
            product.select_one(
                "p.review-count"
            ).text.split()[0]
        )
    )


async def parse_single_computer(computer: BeautifulSoup) -> Product:
    return Product(
        title=computer.select_one("a.title")["title"],
        description=computer.select_one(
            "p.card-text.description"
        ).text.replace(
            "\xa0",
            " "
        ),
        price=float(computer.select_one("h4.price").text.replace("$", "")),
        rating=len(computer.select("span.ws-icon")),
        num_of_reviews=int(
            computer.select_one(
                "p.review-count"
            ).text.split()[0]
        )
    )


async def get_single_page_home_product(page: BeautifulSoup) -> list[Product]:
    home_products = page.select("div.col-lg-9 > div.row > div.col-md-4")
    return [
        await parse_single_home_product(product) for product in home_products
    ]


async def get_single_computer_page(page: BeautifulSoup) -> list[Product]:
    computers = page.select("div.col-lg-9 > div.row > div.col-md-4")
    return [await parse_single_computer(computer) for computer in computers]


async def get_single_phone_page(page: BeautifulSoup) -> list[Product]:
    phones = page.select("div.col-lg-9 > div.row > div.col-md-4")
    return [await get_single_phone(phone) for phone in phones]


def get_all_laptops() -> list[Product]:
    driver = webdriver.Chrome()
    driver.get(LAPTOP_URL)
    cookies = driver.find_element(By.CLASS_NAME, "acceptCookies")
    if cookies:
        cookies.click()
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(1)
    more_button = driver.find_element(
        By.CLASS_NAME,
        "ecomerce-items-scroll-more"
    )
    while more_button:
        try:
            WebDriverWait(
                driver,
                1
            ).until(
                ec.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        "ecomerce-items-scroll-more")
                )
            )
            more_button.click()
            time.sleep(1)
        except Exception as e:
            logging.info(f"An error occurred during laptop scraping {e}")
            break
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    laptop_tag = soup.select(
        "div.container > div.row > div.col-lg-9 > div.row > div.col-md-4"
    )

    return [get_single_laptop(laptop) for laptop in laptop_tag]


def get_all_tablets() -> list[Product]:
    driver = webdriver.Chrome()
    driver.get(TABLETS_URL)
    cookies = driver.find_element(By.CLASS_NAME, "acceptCookies")
    if cookies:
        cookies.click()
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(1)
    more_button = driver.find_element(
        By.CLASS_NAME,
        "ecomerce-items-scroll-more"
    )
    while more_button:
        try:
            WebDriverWait(
                driver,
                1
            ).until(
                ec.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        "ecomerce-items-scroll-more")
                )
            )
            more_button.click()
            time.sleep(1)
        except Exception as e:
            logging.info(f"An error occurred during tablet scraping {e}")
            break
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tablet_tag = soup.select(
        "div.container > div.row > div.col-lg-9 > div.row > div.col-md-4"
    )

    return [get_single_tablet(tablet) for tablet in tablet_tag]


def get_all_touch() -> list[Product]:
    driver = webdriver.Chrome()
    driver.get(TOUCH_URL)
    cookies = driver.find_element(By.CLASS_NAME, "acceptCookies")
    if cookies:
        cookies.click()
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(1)
    more_button = driver.find_element(
        By.CLASS_NAME,
        "ecomerce-items-scroll-more"
    )
    while more_button:
        try:
            WebDriverWait(
                driver,
                1
            ).until(
                ec.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        "ecomerce-items-scroll-more")
                )
            )
            more_button.click()
            time.sleep(1)
        except Exception as e:
            logging.info(f"An error occurred during touch scraping {e}")
            break
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    touch_tag = soup.select(
        "div.container > div.row > div.col-lg-9 > div.row > div.col-md-4"
    )

    return [get_single_tablet(touch) for touch in touch_tag]


async def get_all_home_products(client: AsyncClient) -> list[Product]:
    page = await client.get(HOME_URL)
    first_page = BeautifulSoup(page.content, "html.parser")
    return await get_single_page_home_product(first_page)


async def get_all_computers(client: AsyncClient) -> list[Product]:
    page = await client.get(COMPUTER_URL)
    first_page = BeautifulSoup(page.content, "html.parser")
    return await get_single_computer_page(first_page)


async def get_all_phones(client: AsyncClient) -> list[Product]:
    page = await client.get(PHONE_URL)
    first_page = BeautifulSoup(page.content, "html.parser")
    return await get_single_phone_page(first_page)


async def write_file_to_csv(products: list[Product], file_name: str) -> None:
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(product) for product in products])


async def get_products_without_driver() -> None:
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                (tg.create_task(get_all_home_products(client)), "home.csv"),
                (tg.create_task(get_all_computers(client)), "computers.csv"),
                (tg.create_task(get_all_phones(client)), "phones.csv")
            ]
            for task, filename in tasks:
                data = await task
                await write_file_to_csv(data, filename)


def get_all_products() -> None:
    with pool.ProcessPoolExecutor(3) as executor:
        future_to_task = {
            executor.submit(get_all_laptops): "laptops.csv",
            executor.submit(get_all_tablets): "tablets.csv",
            executor.submit(get_all_touch): "touch.csv"
        }
        for future in pool.as_completed(future_to_task):
            try:
                write_file_to_csv(future.result(), future_to_task[future])
            except Exception as e:
                print(
                    f"An error occurred in "
                    f"{future_to_task[future].split('.')[0]}\n"
                    f"{e}"
                )
    asyncio.run(get_products_without_driver())


if __name__ == "__main__":
    get_all_products()
