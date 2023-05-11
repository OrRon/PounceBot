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
import requests
import time
import random

LOG_PATH = ''
COOKIES_FILE = 'cookies.json'
HEADERS_FILE = 'headers.json'

def load_data_from_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data

LOG_PATH = ''
CONFIDENCE = 0.85
SLEEP_START = 3
SLEEP_END = 12
MOUSE_MOVE_DURATION = 0.25
COORDINATE_FACTOR = 2

screen_width , screen_height = pyautogui.size()


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

def get_next_pos(): ## Make sure not to hover over the buttons
    x = random.randint(0, screen_width - 1)
    y = random.randint(screen_height - 100, screen_height - 1)
    return x , y

def move(duration):
    x,y = get_next_pos()
    print("Moving to ({},{})".format(x,y))
    pyautogui.moveTo(x,y, duration=duration)




def write_to_log(l):
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(json.dumps(l, indent=4) + '\n')
        log_file.close()
    print(l, LOG_PATH)


def random_seconds():
    return random.randint(15, 45)

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
        msg = messages[idx % len(messages)]
        idx = idx + 1
        id = linkedin_profile_url.split('/in/')[1]
        name = linkedin_profile_name.split(' ')[0]
        message_to_send = msg % (name)
        print(message_to_send)
        cmd = browser_cmd % linkedin_profile_url
        os.system(cmd)
        wait_random()
        result = send_request_gui(message_to_send, is_dry_run, CONFIDENCE)
        write_to_log({'profile': linkedin_profile_url, 'message': message_to_send, 'result': result})
        if is_interactive:
            input("<Enter> to proceed")
        build_and_send_request(id,message_to_send)
        random_time = random_seconds()
        print(f"Going to sleep for {random_time} seconds...")
        time.sleep(random_seconds())
        print(f"Woke up after {random_time} seconds!")


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


def build_and_send_request(id,msg):
    cookies = load_data_from_file(COOKIES_FILE)
    headers = load_data_from_file(HEADERS_FILE)

    params = {
        'action': 'verifyQuotaAndCreate',
        'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
    }

    json_data = {
        'inviteeProfileUrn': 'urn:li:fsd_profile:' + id,
        'customMessage': msg,
    }
    response = requests.post(
        'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    print(response.status_code, response.reason, response.text)

def main():
    if platform.system() == "Windows":
        cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" %s'''
        global COORDINATE_FACTOR
        COORDINATE_FACTOR = 1
    else:
        cmd = '''open -a "Google Chrome" %s'''  # FIX_ME - check this works

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="html file path", type=str, required=True)
    parser.add_argument("-i", help="wait for user input between profiles", action='store_true', default=False)
    parser.add_argument("-d", help="Is dry run", action='store_true', default=False)
    parser.add_argument("--network", help="network to use", action='store_true', default=False)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')

    messages = read_messages(config)


    global LOG_PATH
    LOG_PATH = config['general']['log_path']
    global CONFIDENCE
    CONFIDENCE = float(config['general']['confidence'])
    global SLEEP_START
    SLEEP_START = int(config['general']['sleep_start'])
    global SLEEP_END
    SLEEP_END = int(config['general']['sleep_start'])

    print(f'src = [{args.src}]\nchrome_cmd = [{cmd}]\nmessages = [{messages}]')
    entries = {}
    with open(args.src, 'r', encoding='utf8') as file:
        html = file.read()
        entries = parse_html(html)
        print(f'{len(entries)} entries loaded')
        open_browser_for_each_entry(cmd, messages, entries, args.i, args.d)


def wait_random():
    sleep_time = random.randint(SLEEP_START, SLEEP_END)
    print(f"Sleeping {sleep_time} secs")
    for i in range(int(sleep_time / MOUSE_MOVE_DURATION)):
        move(MOUSE_MOVE_DURATION)

def find_img_in_screen(imgs, confidence):
    for i in imgs:
        image_location = pyautogui.locateOnScreen(i, confidence=confidence)
        if image_location:
            image_center = pyautogui.center(image_location)
            return Point(image_center.x / COORDINATE_FACTOR, image_center.y / COORDINATE_FACTOR)
    return False


def send_request_gui(msg, is_dry_run, confidence):
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
            wait_random()
            img_connect = find_img_in_screen(more_connect, confidence)

    if not img_connect:
        return "Couldn't find connect"


    pyautogui.click(img_connect.x, img_connect.y)  # click on connect
    wait_random()
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
