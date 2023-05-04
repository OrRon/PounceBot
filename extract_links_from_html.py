import os
from bs4 import BeautifulSoup
import re
import pyperclip
import argparse
import platform
import configparser


def transform_linkedin_link(link):
    base_link = 'https://www.linkedin.com/in/'
    match = re.search(r"lead\/(.*?),NAME_SEARCH", link)

    if match:
        lead_id = match.group(1)
        return base_link + lead_id
    else:
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


def open_browser_for_each_entry(browser_cmd, messages, entries):
    idx = 0
    for linkedin_profile_url, linkedin_profile_name in entries.items():
        name = linkedin_profile_name.split(' ')[0]
        msg = messages[idx % len(messages)]
        idx = idx + 1
        message_to_send = msg % (name)
        print(message_to_send)
        pyperclip.copy(message_to_send)
        cmd = browser_cmd % linkedin_profile_url
        os.system(cmd)
        input('<Enter> for next entry')

def read_messages(config):
    messages = []
    for i in range(1,10):
        try:
            msg = config['general']['msg' + str(i)]
            msg = msg.replace('<br>', '\n')
            messages.append(msg)
        except:
            pass
    return messages


def main():
    if platform.system() == "Windows":
        cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" %s'''
    else:
        cmd = '''open -a "Google Chrome" %s'''  # FIX_ME - check this works

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="html file path", type=str, required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    messages = read_messages(config)

    print(f'src = [{args.src}]\nchrome_cmd = [{cmd}]\nmessages = [{messages}]')
    entries = {}
    with open(args.src, 'r', encoding='utf8') as file:
        html = file.read()
        entries = parse_html(html)
        print(f'{len(entries)} entries loaded')
        open_browser_for_each_entry(cmd, messages, entries)


if __name__ == '__main__':
    main()
