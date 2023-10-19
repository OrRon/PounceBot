from bs4 import BeautifulSoup
import csv

# Load the HTML file
with open('index.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <a> elements with the specified class
a_elements = soup.find_all('a', class_='ps1-item')

linkedin_records = []

# Iterate over the found <a> elements and extract the data
for a_element in a_elements:
    # Extract name, position, and LinkedIn profile URL
    name_element = a_element.find('h3')
    position_element = a_element.find('p')
    linkedin_profile = a_element['href']

    if name_element and position_element and linkedin_profile:
        full_name = name_element.text.strip()
        reachout_name = full_name.split()[0] if full_name else ''
        position = position_element.text.strip()

        linkedin_records.append({
            'linkedin_profile': linkedin_profile,
            'reachout_name': reachout_name,
            'position': position,
            'full_name': full_name
        })

# Specify the CSV file path
csv_file = 'linkedin_data_from_new_format.csv'

# Write the data to the CSV file
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = ['linkedin_profile', 'reachout_name', 'position', 'full_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(linkedin_records)

print(f"Data has been saved to {csv_file}")

