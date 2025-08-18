from scraping import perform_item_page_scrapping, perform_main_search_page_scrapping
from scraping import set_up_logger
logger = set_up_logger(__name__)
from mongo_manager import MongoManager

mongo_manager: MongoManager = MongoManager()

def main():
    desired_search = input("What are you looking for? ")
    number_of_pages = int(input("How many pages do you want to scrape? "))
    print_results = input("Do you want to print the results? (y/n) ")
    category = input("In what category do you want to clasify the items? ")

    results = perform_main_search_page_scrapping(desired_search, max_pages=number_of_pages)
    logger.info(f"Found {len(results)} results")
    if print_results == "y":
        for idx, result in enumerate(results):
            logger.info(f"Item {idx+1}: {result['title']}")

    mercado_libre_objects = []
    for result in results:
        logger.info(f"Scraping item: {result['title']}")
        item_page_result = perform_item_page_scrapping(result['url'], category)
        logger.info(f"Scraped item: {item_page_result.to_dict()}")
        mercado_libre_objects.append(item_page_result.to_dict())

        if print_results == "y":
            logger.info(f"Item {idx+1}: {item_page_result.to_dict().remove('url')}")

    mongo_manager.insert_many(mercado_libre_objects)
    logger.info(f"Inserted {len(mercado_libre_objects)} mercado libre objects into the database")

if __name__ == "__main__":
    main()