import argparse
from scraping_functions import scrape_collection_data, save_ids_to_file

def main():
    # Create a command-line argument parser
    parser = argparse.ArgumentParser(description="Steam Workshop Collection Crawler CLI")
    parser.add_argument("collection_url", help="URL of the Steam Workshop collection")
    args = parser.parse_args()

    # Get the collection URL from the command-line arguments
    collection_url = args.collection_url

    # Call the function to scrape collection data
    workshop_data_list = scrape_collection_data(collection_url)

    if workshop_data_list:
        # Calculate the total number of collection items
        total_items = len(workshop_data_list)
        print(f"Collection Crawl Complete.\nTotal number of collection items: {total_items}")
    else:
        print("Failed to retrieve data from the collection URL.")

if __name__ == "__main__":
    main()
