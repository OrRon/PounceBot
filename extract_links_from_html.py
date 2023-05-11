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
        log_file.write(json.dumps(l, indent=4) + '\n')
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


def open_browser_for_each_entry(browser_cmd, messages, entries, is_interactive, is_dry_run):
    idx = 0
    for linkedin_profile_url, linkedin_profile_name in entries.items():
        name = linkedin_profile_name.split(' ')[0]
        msg = messages[idx % len(messages)]
        idx = idx + 1
        message_to_send = msg % (name)
        print(message_to_send)
        cmd = browser_cmd % linkedin_profile_url
        os.system(cmd)
        time.sleep(7)
        result = send_request_gui(message_to_send, 0.85,is_dry_run)
        write_to_log({'profile': linkedin_profile_url, 'message': message_to_send, 'result': result})
        if is_interactive:
            input("<Enter> to proceed")


def read_messages(config):
    messages = []
    for i in range(1, 10):
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
    parser.add_argument("-d", help="Is dry run", action='store_true', default=False)
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
        open_browser_for_each_entry(cmd, messages, entries, args.i, args.d)

def find_img_in_screen(imgs, confidence):
    for i in imgs:
        image_location = pyautogui.locateOnScreen(i, confidence=confidence)
        if image_location:
            image_center = pyautogui.center(image_location)
            return image_center
    return False


def send_request_gui(msg, confidence, is_dry_run):
    ## Connect main
    connect_image_main = [os.path.join('img', 'connect_main.png'), os.path.join('img', 'connect_main2.png')]

    ## More + more_connect
    more = [os.path.join('img', 'more.png'),
            os.path.join('img', 'more2.png'),
            os.path.join('img', 'more3.png'),
            os.path.join('img', 'more4.png'),
            os.path.join('img', 'more5.png')]
    more_connect = [os.path.join('img', 'more_connect.png'),]
    ## Add note
    add_note = [os.path.join('img', 'add_note.png'),]
    send = [os.path.join('img', 'send.png'),]


    found_connect = False
    ## Flow 1: there is the main connect button
    img_connect = find_img_in_screen(connect_image_main, confidence)
    if not img_connect:
        img_more = find_img_in_screen(more, confidence)
        if img_more:
            pyautogui.click(img_more.x, img_more.y)
            time.sleep(3)
            img_connect = find_img_in_screen(more_connect, confidence)

    if not img_connect:
        return "Couldn't find connect"


    pyautogui.click(img_connect.x, img_connect.y)  # click on connect
    time.sleep(3)
    ## Send message
    img_add_note = find_img_in_screen(add_note, confidence)

    if not img_add_note:
        return "Couldn't find add note"

    pyautogui.click(img_add_note.x, img_add_note.y)  # click on add_note
    time.sleep(3)
    pyautogui.typewrite(msg)
    time.sleep(3)

    img_send = find_img_in_screen(send, confidence)
    if not img_send:
        return "Couldn't find img_send"
    if is_dry_run:
        return "Success dry run"

    pyautogui.click(img_send.x, img_send.y)  # click on connect
    return "success"


if __name__ == '__main__':
    main()
