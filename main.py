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
    if print_results.lower().strip() == "y":
        for idx, result in enumerate(results):
            logger.info(f"Item {idx+1}: {result['title']}")

    inserted_count = 0
    for result in results:
        logger.info(f"Scraping item: {result['title']}")
        item_page_result = perform_item_page_scrapping(result['url'], category)
        logger.info(f"Scraped item: {item_page_result.to_dict()}")

        mongo_manager.create_document(item_page_result.to_dict())
        inserted_count += 1

        if print_results.strip().lower() == "y":
            item_dict = item_page_result.to_dict()
            item_dict.pop('url', None)
            logger.info(f"Item {idx+1}: {item_dict}")

    logger.info(f"Inserted {len(inserted_count)} mercado libre objects into the database")

if __name__ == "__main__":
    main()