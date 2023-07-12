import os
import openai
import configparser



class OpenAIClient:
    def __init__(self, api_key, org_id):
        print(f"api_key: {api_key[:10]}, org_id: {org_id}")
        openai.organization = org_id
        openai.api_key = api_key
        role_mesage = [{'role': 'system', 'content' : 'You are an expert in secret management for machine to machine communication in enterprises. I will ask you give you descriptions such as "Easily manage your environment variables and secrets" and will ask you to output "true" or "false" if they are very related to machine to machine communication. Do not output anything else apart from "true" or "false"' },]
        example_message = [{'role' : 'user', 'content' : 'Easily manage your environment variables and secrets'},
                           {'role' : 'assistant', 'content' : 'True'},
                           {'role' : 'user', 'content' : 'Making Internet Business Personal'},
                           {'role' : 'assistant', 'content' : 'False'},
                           {'role' : 'user', 'content' : 'A tool for aggregating multiple vaults'},
                           {'role' : 'assistant', 'content' : 'True'},
        ]
        self.messages = role_mesage + example_message


    def is_description_related(self, description):
        if not description or not issubclass(type(description), str) or len(description) < 10:
            return False
        messages = self.messages + [{'role' : 'user', 'content' : description},]
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        return completion.choices[0].message.content.lower() == 'true'

    




def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = open(config['general']['path_to_openai_api_key']).read().strip()
    org_id = config['general']['org_id']
    chat = OpenAIClient(api_key, org_id)
    x = 'A tool for reading secrets from  vaults'
    print(f"desc:{x}, res:{chat.is_description_related(x)}")
    x = 'A tool for planning weddings'
    print(f"desc:{x}, res:{chat.is_description_related(x)}")

if __name__ == "__main__":
    main()