from bs4 import BeautifulSoup
import csv

# Load the HTML file
with open('glilot.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find all elements with class "item team-item show"
team_items = soup.find_all('div')

linkedin_records = []
print(team_items)
# Iterate over the found elements and extract the data
for item in team_items:
    # Extract data
    try:
        full_name = item.find('h2').text.strip()
        job = item.find('div', class_='job').text.strip()

        linkedin_profile = item.find('a', class_='linkedin-link')['href']

        # Extract the first name from the full name
        first_name = full_name.split()[0] if full_name else ''

        if first_name and linkedin_profile:
            linkedin_records.append({'linkedin_profile': linkedin_profile, 'reachout_name': first_name, 'position': job, 'full_name': full_name})
    except:
        print(item)


# Deduplicate the data based on 'linkedin_profile'
deduplicated_data = []
unique_links = set()

for row in linkedin_records:
    linkedin_profile = row['linkedin_profile']
    if linkedin_profile not in unique_links:
        deduplicated_data.append(row)
        unique_links.add(linkedin_profile)



# Specify the CSV file path
csv_file = 'linkedin_data.csv'

# Write the data to the CSV file
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = ['linkedin_profile', 'reachout_name', 'position', 'full_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(deduplicated_data)

print(f"Data has been saved to {csv_file}")

