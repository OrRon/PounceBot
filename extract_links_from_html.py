
import os
from bs4 import BeautifulSoup
import re
import pyperclip


msg = '''Hi %s,

I'm studying the area of Privileged Access and would love to connect and learn from your experience in the field.

Thank you,
~ Or'''


open_b = '''open -a "Google Chrome" %s''' #FIX_ME - check this works

# Open the HTML file
with open('sheet_or.html', 'r', encoding='utf8') as file:
    html = file.read()

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all <a> tags that match the specified format
a_tags = soup.find_all('a', href=re.compile(r"https://www\.linkedin\.com/in/ACwAA\w+"))

# Create a dictionary to store links and their corresponding values
link_dict = {}

# Loop over each <a> tag and add its link and value to the dictionary
for a in a_tags:
    link = a['href']
    value = a.text.strip()
    if value not in link_dict.values():
        link_dict[link] = value

# Print the de-duplicated links and their values
for link, value in link_dict.items():
    name = value.split(' ')[0]
    print (msg % name)
    pyperclip.copy(msg % name)
    print(f"Link: {link}, Value: {value}, Name: {name}")
    cmd = open_b % link
    os.system(cmd)
    input()

