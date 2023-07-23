import argparse
import configparser
import json
import csv
from names_db import NamesDB

NAMES_DB = None


class LogToCSVConvertor:

    def load_source_file(self, path, is_csv):
        if is_csv:
            self.src_data = []
            with open(path, 'r', newline='', encoding='utf8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self.src_data.append(row)
        else:
            self.src_data = json.load(open(path, 'r', encoding='utf8'))

    def __init__(self, owner_name, src_path, csv_path, is_csv):
        self.owner_name = owner_name        
        self.csv_path = csv_path
        self.db = {}
        self.load_source_file(src_path, is_csv)
        print(f"LogToCSVConvertor: {len(self.src_data)} entries in log")
        

    def add_or_update_missing_entries(self, entry):
        key = entry['linkedin_profile_link']
        if key not in self.db: # if the key is not found
            profile = entry['linkedin_profile_link']
            full_name = ''
            reachout_name = entry['reachout_name']
            activity_log = json.dumps([{
                            'result':entry['result'],
                            'type':'linked_in_connect_request',
                            'reachout_by': self.owner_name,
                            'ts':'',
                            'message':entry['message']}])
            reached_out_by = self.owner_name
            self.db[profile] = ({
                'linkedin_profile_link': profile,
                'full_name' : full_name,
                'reachout_name': reachout_name,
                'activity_log': activity_log,
                'reached_out_by': reached_out_by})
        else:
            self.db[key]['activity_log'] = json.dumps(json.loads(self.db[key]['activity_log']) + [{
                            'result':entry['result'],
                            'type':'linked_in_connect_request',
                            'reachout_by': self.owner_name,
                            'ts':'',
                            'message':entry['message']}])
            
    def update_db_from_log(self):
        for e in self.src_data:
            profile = e['profile']
            name = e['message'].split(' ')[1][:-1]
            result = e['result']
            if profile in NAMES_DB:
                name = NAMES_DB[profile][0]
            entry = {'profile': profile,
                                    'reachout_name': name,
                                    'message': e['message'],
                                    'result': result}
            self.add_or_update_missing_entries(entry)

    def update_db_from_csv(self):
        for e in self.src_data:
            key = e['linkedin_profile_link']
            if key not in self.db: ## not in db
                try:
                    json.loads(e['reached_out_by'])
                except:
                    e['reached_out_by'] = json.dumps([e['reached_out_by']])
                self.db[key] = e
            else:   
                activity_log = json.loads(self.db[key]['activity_log']) + json.loads(e['activity_log'])
                reached_out_by = []
                for activity in activity_log:
                    if activity['result'] == 'success' or activity['result'] == 'blocked':
                        reached_out_by.append(activity['reachout_by'])
                self.db[key]['activity_log'] = json.dumps(activity_log)
                self.db[key]['reached_out_by'] = json.dumps(reached_out_by)
    
    def write_csv(self):
        print(f"LogToCSVConvertor: {len(self.db)} entries in csv")
        with open(self.csv_path, 'w', newline='', encoding='utf8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['linkedin_profile_link',
                                                            'full_name',
                                                            'reachout_name',
                                                            'activity_log',
                                                            'reached_out_by'])
            writer.writeheader()
            for e in self.db.values():
                writer.writerow(e)




def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    global NAMES_DB
    NAMES_DB = NamesDB(config['general']['names_db'])
    

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="html file path or log", type=str, required=True)
    parser.add_argument("--dst", help="path to save csv", type=str, required=True)
    parser.add_argument("--is-csv", help="path to save csv", action='store_true', default=False)
    parser.add_argument("--owner-name", help="name of person who the log belong to", type=str, required=True)
    args = parser.parse_args()
    log_to_csv_convertor = LogToCSVConvertor(args.owner_name, args.src, args.dst, args.is_csv)
    if args.is_csv:
        log_to_csv_convertor.update_db_from_csv()
    else:   
        log_to_csv_convertor.update_db_from_log()
    log_to_csv_convertor.write_csv()


if __name__ == '__main__':
    main()