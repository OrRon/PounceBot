import os
from bs4 import BeautifulSoup
import regex as re
import argparse
import platform
import configparser
import time
import pyautogui
import json
import time
import random
import click
import csv
import pyperclip

from names_db import NamesDB
from GoogleSheetClient import GoogleSheetClient

from network import build_and_send_request

LOG_PATH = ''
CONFIDENCE = 0.85
SLEEP_START = 3
SLEEP_END = 12
MOUSE_MOVE_DURATION = 0.25
COORDINATE_FACTOR = 2
NAMES_DB = None
SHEET_CLIENT = None
SCREEN_CAPTURE_REGION = None
TYPE_INTERVAL = 0.1

screen_width , screen_height = pyautogui.size()


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

def get_next_pos(): ## Make sure not to hover over the buttons
    x = random.randint(10, screen_width - 10)
    y = random.randint(screen_height - 100, screen_height - 10)
    return x , y

def move(duration):
    x,y = get_next_pos()
    pyautogui.moveTo(x,y, duration=duration)




def write_to_log(l):
    with open(LOG_PATH, 'a+') as log_file:
        log_file.write(json.dumps(l, indent=4) + ',\n')
        log_file.close()
    SHEET_CLIENT.add_or_update_missing_entries(l)


def random_seconds():
    return random.randint(15, 45)

def contains_only_letters(word):
    pattern = r'^\p{L}{3,}$'
    if re.match(pattern, word, re.UNICODE) is None:
        return False
    if re.match(r'^[A-Z]+$', word):
        return False
    return True
    

def transform_linkedin_username(a_text, link):
    striped = a_text.strip()
    name = striped.split(' ')[0]
    if contains_only_letters(name):
        return name
    
    print(f"a_text: {a_text}")
    print(f"striped: {striped}")
    print(f"name: {name}")
    
    if link in NAMES_DB:
        name = NAMES_DB[link][0]
        print(f"using name from db: {name}")
        return name # Use the name from the database if it exists
    name = input("Enter name: ")
    NAMES_DB[link] = (name, a_text)
    print("Added to database.: [{link}, {name}]")
    return name




def transform_linkedin_link(link):
    base_link = 'https://www.linkedin.com/in/'
    match = re.search(r"lead\/(.*?),NAME_SEARCH", link)

    if match:
        lead_id = match.group(1)
        return base_link + lead_id
    else:
        return link


def parse_html(html, start, end):
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all <a> tags that match the specified format
    a_tags = soup.find_all('a', href=re.compile(r"https://www\.linkedin\.com/(?!.*company)"))

    profiles_ordered = []
    for a in a_tags:
        link = transform_linkedin_link(a['href'])
        if link not in profiles_ordered:
            profiles_ordered.append(link)

    profiles_ordered = profiles_ordered[start:end] # Get the profiles we want
    print(f"Amount of profiles: {len(profiles_ordered)}")

    # Create a dictionary to store links and their corresponding values
    link_dict = {}

    # Loop over each <a> tag and add its link and value to the dictionary
    for a in a_tags:
        link = transform_linkedin_link(a['href'])
        print(link)
        if link in profiles_ordered and link not in link_dict.keys():
            value = transform_linkedin_username(a.text, link)
            link_dict[link] = value

    print(f"Amount of entries: {len(link_dict)}")
    return link_dict


def send_with_random(cmd,message_to_send, is_dry_run, linkedin_profile_url, reachout_name):
    os.system(cmd)
    wait_random()
    result = send_request_gui(message_to_send, is_dry_run, CONFIDENCE)
    write_to_log({'profile': linkedin_profile_url, 'message': message_to_send, 'result': result, 'reachout_name' : reachout_name})


def send_by_method_for_each_entry(browser_cmd, messages, entries, is_interactive, is_dry_run, is_network_run, is_just_log):
    idx = 0
    
    with click.progressbar(range(len(entries.items())), show_pos=True, width=70) as bar:
        for linkedin_profile_url, linkedin_profile_name in entries.items():
            click.clear()
            bar.update(1)
            click.echo("\r\n")
            msg = messages[idx % len(messages)]
            idx = idx + 1
            id = linkedin_profile_url.split('/in/')[1]
            name = linkedin_profile_name
            message_to_send = msg % (name)
            click.secho("[Message]", bold=True, fg='green')
            click.secho(message_to_send)
            cmd = browser_cmd % linkedin_profile_url
            if is_network_run:
                click.secho("[URL]", bold=True, fg='green')
                click.secho(linkedin_profile_url)
                
                ret_code = build_and_send_request(id,message_to_send)
                if ret_code != 200:
                    click.secho(f"Error, return code:{ret_code}", fg='red')
                    return
            elif is_just_log:
                write_to_log({'profile': linkedin_profile_url, 'message': message_to_send, 'result': 'success', 'reachout_name': name})
            else:
                send_with_random(cmd,message_to_send, is_dry_run, linkedin_profile_url, name)
        
            if is_interactive:
                input("<Enter> to proceed")

def load_from_sheet(sheet_name, path_to_credentials, start, end, current_user):
    sheet_c = GoogleSheetClient(path_to_credentials,'reachout_script_db',sheet_name,current_user)
    entries = sheet_c.sheet.get_all_records()
    result = {}
    for entry in entries[start: end]:
        link = entry['linkedin_profile_link']
        result[link] = entry['reachout_name']

    return result

def load_from_csv(data, start, end, current_user):
    # Start by gathering all of the profiles which the current user didn't reach out to.
    filtered_list = []
    for entry in data:
        reached_out_by = json.loads(entry['reached_out_by'])
        was_successful = entry['was_successful'] == '1'
        if not was_successful and current_user not in reached_out_by:
            filtered_list.append(entry)

    print(f"Amount of profiles: {len(filtered_list)}")
    result = {}
    for entry in filtered_list[start: end]:
        link = entry['linkedin_profile_link']
        result[link] = entry['reachout_name']

    return result
    

    


def load_from_log(json_log):
    ## start by de-duping, there might be a case a profile appears twice, and one of them was successful
    json_dict = {}
    for entry in json_log:    
        link = entry['profile']
        value = entry['message'].split(' ')[1][:-1] # Get the first name from the message, remove comma
        if link in json_dict and json_dict[link][2] != 'success':
            json_dict[link] = (link, value, entry['result'])
        elif link not in json_dict:
            json_dict[link] = (link, value, entry['result'])

    
    link_dict = {}
    for entry in json_dict.values():
        print(entry)
        if entry[2] != 'success' and "verified email constraint" not in entry[2]:    
            link_dict[entry[0]] = entry[1]
    return link_dict    


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


def type(text: str):    
    pyperclip.copy(text)
    if platform.system() == "Darwin":
        pyautogui.hotkey("command", "v")
    else:
        pyautogui.hotkey("ctrl", "v")

def print_state(args, config, entries, cmd):
    print('''
    
  _________            .__        __      _________ __          __          
 /   _____/ ___________|__|______/  |_   /   _____//  |______ _/  |_  ____  
 \_____  \_/ ___\_  __ \  \____ \   __\  \_____  \\   __\__  \\   __\/ __ \ 
 /        \  \___|  | \/  |  |_> >  |    /        \|  |  / __ \|  | \  ___/ 
/_______  /\___  >__|  |__|   __/|__|   /_______  /|__| (____  /__|  \___  >
        \/     \/         |__|                  \/           \/          \/ 

    ''')
    
    print(f"NamesDB: {NAMES_DB}")
    print("------------------------------------------")
    print(f"Entries count: {len(entries)}")
    print(f"Source file: {args.src}") 
    print(f"Start index: {args.start}")
    print(f"End index: {args.end}")
    print(f"Is interactive: {args.i}")
    print(f"Is dry run: {args.d}")
    print(f"Is network run: {args.network}")
    print(f"Amount of profiles: {len(entries)}")
    print(f"Messages: {read_messages(config)}")
    print(f"Browser command: {cmd}")
    print(f"Log file: {LOG_PATH}")
    print(f"Confidence: {CONFIDENCE}")
    print(f"Coordinates factor: {COORDINATE_FACTOR}")
    
    print(f"Sleep start: {SLEEP_START}")
    print(f"Sleep end: {SLEEP_END}")
    print(f"Screen capture region: {SCREEN_CAPTURE_REGION}")
    return

def main():
    if platform.system() == "Windows":
        cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" %s'''
        global COORDINATE_FACTOR
        COORDINATE_FACTOR = 1
    elif platform.system() == 'Linux':
        COORDINATE_FACTOR = 1
        cmd = 'google-chrome %s &'
    else:
        cmd = '''open -a "Google Chrome" %s'''  # FIX_ME - check this works

    src_type = ['csv', 'log', 'html', 'sheet']
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="html file path or log", type=str, required=True)
    parser.add_argument("--src-type", help="source file type, choose from"  + str(src_type) ,choices = src_type, required=True)
    parser.add_argument("-i", help="wait for user input between profiles", action='store_true', default=False)
    parser.add_argument("-d", help="Is dry run", action='store_true', default=False)
    parser.add_argument("--network", help="network to use", action='store_true', default=False)
    parser.add_argument("--just-log", help="just log, dont sent anything", action='store_true', default=False)
    parser.add_argument("--start", help="index to start from", type=int, default=0)
    parser.add_argument("--end", help="index to stop at", type=int, default=None)
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
    SLEEP_END = int(config['general']['sleep_end'])
    global NAMES_DB
    NAMES_DB = NamesDB(config['general']['names_db'])
    global SHEET_CLIENT
    SHEET_CLIENT = GoogleSheetClient(config['general']['path_to_credentials'],'reachout_script_db','main',config['general']['name'])
    
    if 'screen_capture_region' in config['general']:
        global SCREEN_CAPTURE_REGION
        side_len = int(config['general']['screen_capture_region'])
        SCREEN_CAPTURE_REGION = (0,0,side_len // COORDINATE_FACTOR,side_len // COORDINATE_FACTOR)
    
    global TYPE_INTERVAL
    TYPE_INTERVAL = float(config['general']['type_interval'])
    entries = {}

    if args.src_type == 'html':
        file = open(args.src, 'r', encoding='utf8')
        html = file.read()
        file.close()
        entries = parse_html(html, args.start, args.end)
    elif args.src_type == 'log':
        try:
            file = open(args.src, 'r', encoding='utf8')
            json = file.read()
            file.close()
            entries = load_from_log(json.loads(html))
        except Exception as e:
            print(f"Error parsing json: {e}")
            print("If you are trying to load the log, can you verify it is valid JSON?")
            print("You probably need to remove a ']' from the middle of the file and add it and the end")
    elif args.src_type == 'csv':
        file = open(args.src, 'r', encoding='utf8')
        entries = load_from_csv(csv.DictReader(file), args.start, args.end, config['general']['name'])
        file.close()
    elif args.src_type == 'sheet':
        entries = load_from_sheet(args.src, config['general']['path_to_credentials'],args.start, args.end, config['general']['name'])

    
    
    print(f'{len(entries)} entries loaded')
    print_state(args, config, entries, cmd)
    if input("Continue? [y/n]") != 'y':
        return
    send_by_method_for_each_entry(cmd, messages, entries, args.i, args.d, args.network, args.just_log)


def wait_random():
    sleep_time = random.randint(SLEEP_START, SLEEP_END)
    print(f"Sleeping {sleep_time} secs")
    for i in range(int(sleep_time / MOUSE_MOVE_DURATION)):
        move(MOUSE_MOVE_DURATION)

def find_img_in_screen(imgs, confidence):
    for i in imgs:
        image_location = None
        if SCREEN_CAPTURE_REGION:
            image_location = pyautogui.locateOnScreen(i, confidence=confidence, region = SCREEN_CAPTURE_REGION)
        else:
            image_location = pyautogui.locateOnScreen(i, confidence=confidence)

        if image_location:
            image_center = pyautogui.center(image_location)
            return Point(image_center.x / COORDINATE_FACTOR, image_center.y / COORDINATE_FACTOR)
    return False


def send_request_gui(msg, is_dry_run, confidence):
    ## Connect main
    connect_image_main = [os.path.join('img', 'connect_main.png'), 
                          os.path.join('img', 'connect_main2.png'),
                          os.path.join('img', 'connect_main3.png'),
                          os.path.join('img', 'connect_main4.png'),
                          os.path.join('img', 'connect_main_mac.png'),]

    ## More + more_connect
    more = [os.path.join('img', 'more.png'),
            os.path.join('img', 'more2.png'),
            os.path.join('img', 'more3.png'),
            os.path.join('img', 'more4.png'),
            os.path.join('img', 'more5.png'),
            os.path.join('img', 'more6.png'),
            os.path.join('img', 'more7.png'),
            os.path.join('img', 'more8.png'),
            os.path.join('img', 'more_mac1.png'),]
    more_connect = [os.path.join('img', 'more_connect.png'),
                    os.path.join('img', 'more_connect2.png'),
                    os.path.join('img', 'more_connet_mac.png')
                    ,]
    more_pending = [os.path.join('img', 'more_pending.png'),
                    ]


    ## Blocked
    blocked = [os.path.join('img', 'blocked.png'),]

    ## Add note
    add_note = [os.path.join('img', 'add_note.png'),
                os.path.join('img', 'add_note2.png'),
                os.path.join('img', 'add_note3.png'),
                os.path.join('img', 'add_note4.png'),
                os.path.join('img', 'add_note_mac.png'),
                ]
    send = [os.path.join('img', 'send.png'),
            os.path.join('img', 'send2.png'),
            os.path.join('img', 'send_mac.png'),]


    found_connect = False
    ## Flow 1: there is the main connect button
    img_connect = find_img_in_screen(connect_image_main, confidence)
    if not img_connect:
        img_more = find_img_in_screen(more, confidence)
        if img_more:
            pyautogui.click(img_more.x, img_more.y)
            wait_random()
            img_more_pending = find_img_in_screen(more_pending, confidence)
            if img_more_pending:
                return "pending"
            img_connect = find_img_in_screen(more_connect, confidence)

    if not img_connect:
        return "Couldn't find connect"


    pyautogui.click(img_connect.x, img_connect.y)  # click on connect
    wait_random()

    ## Check if blocked

    img_blocked = find_img_in_screen(blocked, confidence)
    if img_blocked:
        return "blocked"

    ## Send message
    img_add_note = find_img_in_screen(add_note, confidence)

    if not img_add_note:
        return "Couldn't find add note"

    pyautogui.click(img_add_note.x, img_add_note.y)  # click on add_note
    time.sleep(3)
    type(msg)
    time.sleep(3)

    img_send = find_img_in_screen(send, confidence)
    if not img_send:
        return "Couldn't find img_send"
    if is_dry_run:
        return "success-dry-run"

    pyautogui.click(img_send.x, img_send.y)  # click on connect
    return "success"


if __name__ == '__main__':
    main()

