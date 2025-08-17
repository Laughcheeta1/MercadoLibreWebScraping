from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from logging_config import set_up_logger

logger = set_up_logger(__name__)

class WebDriverType(Enum):
    CHROME = 'chrome'
    EDGE = 'edge'
    FIREFOX = 'firefox'
    SAFARI = 'safari'
    INTERNET_EXPLORER = 'internet explorer'


def perform_mercadolibre_scrapping(search_query, driver_path='/usr/bin/chromedriver', web_driver_type=WebDriverType.CHROME, max_pages=10):    
    """
    Perform a scrapping of the first 10 pages of the search query in mercado libre.
    Args:
        search_query: The query to search for.
        driver_path: The path to the driver.
        web_driver_type: The type of web driver to use.
        max_pages: The maximum number of pages to scrape. If -1, it will scrape all the pages.
    Returns:
        A list of dictionaries with the title and url of the items.
    """
    logger.info(f"Starting MercadoLibre scrapping with query: {search_query}")
    logger.debug(f"Driver path: {driver_path}, Web driver type: {web_driver_type}, Max pages: {max_pages}")
    
    service = Service(driver_path)
    if web_driver_type == WebDriverType.CHROME:
        driver = webdriver.Chrome(service=service)
    elif web_driver_type == WebDriverType.EDGE:
        driver = webdriver.Edge(service=service)
    elif web_driver_type == WebDriverType.FIREFOX:
        driver = webdriver.Firefox(service=service)
    elif web_driver_type == WebDriverType.SAFARI:
        driver = webdriver.Safari(service=service)
    elif web_driver_type == WebDriverType.INTERNET_EXPLORER:
        driver = webdriver.Ie(service=service)
    else:
        raise ValueError(f"Web driver type {web_driver_type} not supported")

    driver.get('https://www.mercadolibre.com.co/')  # Get the default page of mercado libre
    logger.info("Navigated to MercadoLibre homepage")

    # Espera hasta que el input esté presente
    wait = WebDriverWait(driver, 10)
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="cb1-edit"]')))

    # Escribe en el campo de búsqueda
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.ENTER)
    logger.info(f"Search query '{search_query}' submitted")

    # Go through the first 10 pages
    for page_num in range(0, max_pages):
        logger.info(f"Processing page {page_num + 1} of {max_pages}")
        
        # Espera a que carguen los resultados
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ui-search-layout__item')))

        # Parsear con BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Selecciona todos los items
        items = soup.select('li.ui-search-layout__item')
        logger.debug(f"Found {len(items)} items on page {page_num + 1}")

        for item in items:
            # Selecciona el enlace del título con clase poly-component__title
            link = item.select_one('a.poly-component__title')
            if link:
                titulo = link.text.strip()
                href = link.get('href')
                logger.info(f'Título: {titulo}')
                logger.info(f'URL: {href}')

        # Go to the next page
        try:
            logger.debug("Attempting to navigate to next page")
            next_page_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root-app"]/div/div[2]/section/div[6]/nav/ul/li[12]/a')))
            driver.execute_script("arguments[0].click();", next_page_button)
            logger.info(f"Successfully navigated to page {page_num + 2}")
        except:
            logger.warning("Next page button not found, stopping pagination")
            break
        
    logger.info("Finished webscrapping all pages")
    driver.quit()
