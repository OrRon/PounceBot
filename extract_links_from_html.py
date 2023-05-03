import os
from bs4 import BeautifulSoup
import re
import pyperclip
import argparse
import platform

def transform_linkedin_link(link):
    base_link = 'https://www.linkedin.com/in/'
    match = re.search(r"lead\/(.*?),NAME_SEARCH", link)

    if match:
        lead_id = match.group(1)
        print("Lead ID:", lead_id)
        return base_link + lead_id
    else:
        print("No match found")
        return link

def parse_html(html):
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all <a> tags that match the specified format
    a_tags = soup.find_all('a', href=re.compile(r"https://www\.linkedin\.com/(?!.*company)"))

    # Create a dictionary to store links and their corresponding values
    link_dict = {}

    # Loop over each <a> tag and add its link and value to the dictionary
    for a in a_tags:
        link = transform_linkedin_link(a['href'])
        value = a.text.strip()
        print(link)
        if link not in link_dict.keys():
            link_dict[link] = value

    return link_dict


def open_browser_for_each_entry(browser_cmd, msg, my_name, entries):
    for linkedin_profile_url, linkedin_profile_name in entries.items():
        name = linkedin_profile_name.split(' ')[0]
        message_to_send = msg % (name, my_name)
        print(message_to_send)
        pyperclip.copy(message_to_send)
        cmd = browser_cmd % linkedin_profile_url
        os.system(cmd)
        input('<Enter> for next entry')


def main():
    msg = '''Hi %s,

    I'm studying the area of Privileged Access and would love to connect and learn from your experience in the field.

    Thank you,
    ~ %s'''
    
    if platform.system() == "Windows":
        cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" %s'''
    else:
        cmd = '''open -a "Google Chrome" %s'''  # FIX_ME - check this works

    parser = argparse.ArgumentParser()
    parser.add_argument("--my_name", help="Your name", type=str, required=True)
    parser.add_argument("--src", help="html file path", type=str, required=True)
    args = parser.parse_args()

    print(f'src = [{args.src}]\nmy_name = [{args.my_name}]\nchrome_cmd = [{cmd}]\nmsg = [{msg}]')
    entries = {}
    with open(args.src, 'r', encoding='utf8') as file:
        html = file.read()
        entries = parse_html(html)
        print(f'{len(entries)} entries loaded')
        open_browser_for_each_entry(cmd, msg, args.my_name, entries)


if __name__ == '__main__':
    main()
