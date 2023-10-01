import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm

def create_data_folder():
    data_folder = "data"
    crawled_data_folder = "crawledData"

    # Create the "data" folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    count = 1
    while os.path.exists(os.path.join(data_folder, f"{crawled_data_folder}_{count}")):
        count += 1
    new_folder = os.path.join(data_folder, f"{crawled_data_folder}_{count}")
    os.makedirs(new_folder)

    return new_folder

def scrape_collection_data(collection_url):
    response = requests.get(collection_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        collection_items = soup.find_all("div", {"class": "collectionItem"})

        all_data = []  # Store each workshop item's data as a separate dictionary
        mod_ids = set()   # Initialize sets for Mod IDs, Workshop IDs, Cell values, and Map Folder values
        workshop_ids = set()
        cell_values = []
        map_folder_values = []

        print("Starting Collection Crawl")

        # Add tqdm to track progress
        progress_bar = tqdm(total=len(collection_items), unit=" item(s)")

        for item in collection_items:
            item_details = item.find("div", {"class": "collectionItemDetails"})
            workshop_link = item_details.find("a", href=True)

            if workshop_link:
                workshop_url = workshop_link["href"]

                workshop_data = scrape_workshop_data(workshop_url)
                if workshop_data:
                    all_data.append(workshop_data)  # Append each item's data as a separate dictionary

                    # Add Mod IDs, Workshop IDs, Cell values, and Map Folder values to the sets if they exist
                    mod_ids.update(workshop_data.get("Mod IDs", []))
                    workshop_ids.update(workshop_data.get("Workshop IDs", []))
                    cell = workshop_data.get("Cell")
                    if cell:
                        cell_values.append(cell)
                    map_folder = workshop_data.get("Map Folder")
                    if map_folder:
                        map_folder_values.append(map_folder)

            progress_bar.update(1)  # Update the progress bar

        progress_bar.close()  # Close the progress bar

        data_folder = create_data_folder()

        # Save Mod IDs, Workshop IDs, Cell values, and Map Folder values to separate files using the save_ids_to_file function
        if mod_ids:
            save_ids_to_file(data_folder, "modIDs.txt", mod_ids)
        if workshop_ids:
            save_ids_to_file(data_folder, "workshopItemIDs.txt", workshop_ids)
        if cell_values:
            save_ids_to_file(data_folder, "cell.txt", cell_values)
        if map_folder_values:
            save_ids_to_file(data_folder, "mapFolders.txt", map_folder_values)

        # Save the scraped data as a JSON file
        with open(os.path.join(data_folder, "scraped_data.json"), "w") as json_file:
            json.dump(all_data, json_file, indent=4)  # Write data to JSON file

        return all_data  # Return the list of workshop items' data
    else:
        return []

def scrape_workshop_data(workshop_url):
    response = requests.get(workshop_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        description_div = soup.find("div", {"class": "workshopItemDescription"})

        workshop_ids = []
        mod_ids = []
        map_folders = []
        cells = []
        title = soup.find("div", {"class": "workshopItemTitle"}).get_text().strip()
        map_folder = None  # Initialize map_folder to None
        cell = None  # Initialize cell to None

        for text in description_div.stripped_strings:
            if text.startswith("Workshop ID:"):
                workshop_id = text.replace("Workshop ID:", "").strip()
                workshop_ids.append(workshop_id)
            elif text.startswith("Mod ID:"):
                mod_id = text.replace("Mod ID:", "").strip()
                mod_ids.append(mod_id)
            elif text.startswith("Map Folder:"):
                map_folder = text.replace("Map Folder:", "").strip()
                map_folders.append(map_folder)  # Append to the list
            elif text.startswith("Cell:"):
                cell = text.replace("Cell:", "").strip()
                cells.append(cell)  # Append to the list

        # Check if cell and map_folder were assigned, otherwise set them to None
        if cell is None:
            cell = None
        if map_folder is None:
            map_folder = None

        return {
            "Title": title,
            "Workshop IDs": workshop_ids,
            "Mod IDs": mod_ids,
            "Map Folder": map_folder,
            "Cell": cell
        }
    else:
        return {}

def save_ids_to_file(folder, filename, data):
    ids_file = os.path.join(folder, filename)
    with open(ids_file, "w") as file:
        for item in data:
            file.write(f"{item};")

if __name__ == "__main__":
    collection_url = input("Enter the Steam Workshop Collection URL: ")
    scrape_collection_data(collection_url)
