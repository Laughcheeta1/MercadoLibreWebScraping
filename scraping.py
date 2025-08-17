from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from logging_config import set_up_logger
from mercado_libre import Mercado_Libre_Object

logger = set_up_logger(__name__)

class WebDriverType(Enum):
    CHROME = 'chrome'
    EDGE = 'edge'
    FIREFOX = 'firefox'
    SAFARI = 'safari'
    INTERNET_EXPLORER = 'internet explorer'


def perform_main_search_page_scrapping(search_query, driver_path='/usr/bin/chromedriver', web_driver_type=WebDriverType.CHROME, max_pages=10):    
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

    results = []

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


def perform_item_page_scrapping(url, driver_path='/usr/bin/chromedriver', web_driver_type=WebDriverType.CHROME):
    """
    Perform a scrapping of the item page in mercado libre.
    Args:
        url: The url of the item page.
        driver_path: The path to the driver.
        web_driver_type: The type of web driver to use.
    Returns:
        A Mercado_Libre_Object with the item information.
    """
    logger.info(f"Starting MercadoLibre item page scrapping with url: {url}")
    logger.debug(f"Driver path: {driver_path}, Web driver type: {web_driver_type}")
    
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
    
    try:
        driver.get(url)
        logger.info(f"Navigated to item page: {url}")
        
        # Wait for main container to load (single wait)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pdp-container__col')))
        
        # Get page source once after page loads
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract required data using BeautifulSoup
        
        # Title
        title_elem = soup.find('h1', class_='ui-pdp-title')
        title = title_elem.text.strip() if title_elem else None
        logger.info(f"Title: {title}")
        
        # Price (current price) - convert to float
        price_elem = soup.find('span', class_='andes-money-amount__fraction')
        price_text = price_elem.text.strip() if price_elem else "0"
        # Remove dots (thousand separators) and convert to float
        price = float(price_text.replace('.', '').replace(',', '.')) if price_text else 0.0
        logger.info(f"Price: {price}")
        
        # Currency
        currency = _get_currency_from_url(url)
        logger.info(f"Currency: {currency}")
        
        # Condition
        subtitle_elem = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_elem:
            subtitle_text = subtitle_elem.text.strip()
            condition = _extract_condition_from_text(subtitle_text)
        else:
            condition = "Unknown"
        logger.info(f"Condition: {condition}")
        
        # Seller ID/Name
        seller_name = None
        seller_elem = soup.find('div', class_='ui-pdp-seller__header__title')
        if seller_elem:
            seller_button = seller_elem.find('button')
            if seller_button:
                seller_spans = seller_button.find_all('span')
                seller_name = seller_spans[1].text.strip() if len(seller_spans) > 1 else None
        logger.info(f"Seller NAME: {seller_name}")
        
        # First image URL
        first_image_url = None
        image_elem = soup.find('img', class_='ui-pdp-image ui-pdp-gallery__figure__image')
        if image_elem:
            first_image_url = image_elem.get('src') or image_elem.get('data-src')

        logger.info(f"First image URL: {first_image_url}")
        
        # Create and return Mercado_Libre_Object
        result = Mercado_Libre_Object(
            title=title,
            url=url,
            price=price,
            currency=currency,
            condition=condition,
            seller_name=seller_name,
            first_image_url=first_image_url
        )
        
        logger.info(f"Result object: {result.to_dict()}")
        return result
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise
    finally:
        driver.quit()
        logger.info("Driver closed")


def _get_currency_from_url(url):
    """
    Get the currency given the country in the url.
    Args:
        url: The url of the item page.
    Returns:
        The currency of the item.
    """
    if "co" in url.lower():
        return "COP"
    if "cl" in url.lower():
        return "CLP"
    if "mxn" in url.lower():
        return "MXN"
    else:
        return "COP"


def _extract_condition_from_text(text):
    """
    Extract the condition from the text.
    Args:
        text: The text to extract the condition from.
    Returns:
        The condition of the item.
    """
    return text.split("|")[0].strip()


if __name__ == "__main__":
    result = perform_item_page_scrapping("https://articulo.mercadolibre.com.co/MCO-1553683955-pasamontanas-moto-multiuso-6-en-1-balaclava-termico-ciclismo-_JM?variation=187175282169#reco_item_pos=0&reco_backend=item_decorator&reco_backend_type=function&reco_client=home_items-decorator-legacy&reco_id=ce6ed4a1-7ad8-4c43-9f81-48f733719558&reco_model=&c_id=/home/navigation-recommendations-seed/element&c_uid=25eb598b-7bee-43da-899e-d62cb4a63219&da_id=navigation&da_position=0&id_origin=/home/dynamic_access&da_sort_algorithm=ranker")
    print(result.to_dict())