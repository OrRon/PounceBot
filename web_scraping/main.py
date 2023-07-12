import configparser
import argparse
import csv
import click
import pandas as pd

from OpenAIClient import OpenAIClient
from GoogleSheetClient import GoogleSheetClient



def write_to_log(l):
    with open(LOG_PATH, 'a+') as log_file:
        log_file.write(json.dumps(l, indent=4) + ',\n')
        log_file.close()


def print_state(args, config, entries):
    print('''
    
  _________            .__        __      _________ __          __          
 /   _____/ ___________|__|______/  |_   /   _____//  |______ _/  |_  ____  
 \_____  \_/ ___\_  __ \  \____ \   __\  \_____  \\   __\__  \\   __\/ __ \ 
 /        \  \___|  | \/  |  |_> >  |    /        \|  |  / __ \|  | \  ___/ 
/_______  /\___  >__|  |__|   __/|__|   /_______  /|__| (____  /__|  \___  >
        \/     \/         |__|                  \/           \/          \/ 

    ''')
    
    print("------------------------------------------")
    print(f"Entries count: {len(entries)}")
    return



def filter_entries(df, chat):
    #df.assign(relevant=lambda x: chat.is_description_related("'" + x.Description + "'"))
    res = []
    with click.progressbar(range(len(df.Description.values)), show_pos=True, width=70) as bar:
        for desc in df.Description.values:
            click.clear()
            bar.update(1)
            click.echo("\r\n")
            click.secho("[Description]", bold=True, fg='green')
            click.secho(desc)
            res.append(chat.is_description_related(desc))
    
    df['Relevant'] = res

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = open(config['general']['path_to_openai_api_key']).read().strip()
    org_id = config['general']['org_id']

    global LOG_PATH
    LOG_PATH = config['general']['log_path']

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="csv src file", type=str, required=True)
    parser.add_argument("--out", help="path to output", type=str, default='out.csv')

    args = parser.parse_args()

    
    df_entries  = pd.read_csv(args.src)
    chat = OpenAIClient(api_key, org_id)

    print_state(args, config, df_entries)
    filter_entries(df_entries, chat)
    df_final = df_entries#df_entries.drop(columns=['Logo', 'Logo HTML'])
    df_final.to_csv(args.out)

if __name__ == '__main__':
    main()
