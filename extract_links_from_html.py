import os
from bs4 import BeautifulSoup
import re
import pyperclip
import argparse
import platform
import configparser
import time
import pyautogui
import json

LOG_PATH = ''


def write_to_log(l):
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(json.dumps(l, indent = 4) + '\n')
        log_file.close()
    print(l, LOG_PATH)


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


def open_browser_for_each_entry(browser_cmd, messages, entries, is_interactive):
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
        time.sleep(7)
        result = send_request_gui(message_to_send)
        write_to_log({'profile': linkedin_profile_url,  'message': message_to_send, 'result' : result})
        if is_interactive:
            input("<Enter> to proceed")

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
    parser.add_argument("-i", help="wait for user input between profiles", action='store_true', default=False)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    messages = read_messages(config)

    global LOG_PATH
    LOG_PATH = config['general']['log_path']

    print(f'src = [{args.src}]\nchrome_cmd = [{cmd}]\nmessages = [{messages}]')
    entries = {}
    with open(args.src, 'r', encoding='utf8') as file:
        html = file.read()
        entries = parse_html(html)
        print(f'{len(entries)} entries loaded')
        open_browser_for_each_entry(cmd, messages, entries, args.i)


def send_request_gui(msg):
    click_order_connect1 = [os.path.join('img', 'more.png'), os.path.join('img', 'more_connect.png')]
    click_order_connect2 = [os.path.join('img', 'connect_main.png')]

    click_send_msg = [os.path.join('img','add_note.png'), os.path.join('img','send.png')]

    print(msg)

    ## Connect

    image_location = pyautogui.locateOnScreen(click_order_connect2[0])
    if image_location:
        image_center = pyautogui.center(image_location)
        pyautogui.click(image_center.x, image_center.y)
    else:
        image_location = pyautogui.locateOnScreen(click_order_connect1[0])
        if image_location:
            image_center = pyautogui.center(image_location)
            pyautogui.click(image_center.x, image_center.y)
            time.sleep(0.5)
            image_location = pyautogui.locateOnScreen(click_order_connect1[1])
            if image_location:
                image_center = pyautogui.center(image_location)
                pyautogui.click(image_center.x, image_center.y)
            else:
                return "unable to find the more_connect button"
    ## Send a message if required


    print("Attempting to send a message")
    time.sleep(3)
    image_location = pyautogui.locateOnScreen(click_send_msg[0])
    if image_location:
        print("Found add a note")
        image_center = pyautogui.center(image_location)
        pyautogui.click(image_center.x, image_center.y)

        time.sleep(3)
        pyautogui.typewrite(msg)
        time.sleep(2)

        image_location = pyautogui.locateOnScreen(click_send_msg[1])
        if image_location:
            image_center = pyautogui.center(image_location)
            pyautogui.click(image_center.x, image_center.y)
            return "success"
        else:
            return "Couldn't find send:" + click_send_msg[1]
    else:
        return "Couldn't find add a note"
    return "failed"

if __name__ == '__main__':
    main()
