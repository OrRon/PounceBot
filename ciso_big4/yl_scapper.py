from bs4 import BeautifulSoup
import re
import json
import csv

# Load the HTML file
with open('yl.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <script> elements with the specified pattern
scripts = soup.find_all('script', text=re.compile(r'window\.members\[\'.+\'\] = {'))

linkedin_records = []

# Iterate over the found scripts and extract the JSON data
for script in scripts:
    script_text = script.string
    # Extract the JSON data within the script
    data_match = re.search(r'window\.members\[\'.+\'\] = ({.*?});', script_text)
    if data_match:
        data_json = data_match.group(1)
        member_data = json.loads(data_json)
        # Extract data
        linkedin_profile = member_data.get('links', {}).get('linkedin', '')
        position = member_data.get('position', '')
        
        # Extract the first name from the post_title
        full_name = member_data.get('title', '')
        first_name = full_name.split()[0] if full_name else ''

        if linkedin_profile and first_name and position:
            linkedin_records.append({'linkedin_profile': linkedin_profile, 'reachout_name': first_name, 'position': position, 'full_name': full_name})
# Specify the CSV file path
csv_file = 'linkedin_data.csv'

# Write the data to the CSV file
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = ['linkedin_profile', 'reachout_name', 'position', 'full_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(linkedin_records)

print(f"Data has been saved to {csv_file}")

