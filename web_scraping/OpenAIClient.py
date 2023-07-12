import os
import openai
import configparser



class OpenAIClient:

    def __init__(self, prompt):
        config = configparser.ConfigParser()
        config.read('config.ini')
        openai.api_key = open(config['general']['path_to_openai_api_key']).read().strip()
        openai.organization = org_id = config['general']['org_id']
        self.messages = prompt
        print(__class__, self.messages)



    def is_description_related(self, description):
        if not description or not issubclass(type(description), str) or len(description) < 10:
            return False
        messages = self.messages + [{'role' : 'user', 'content' : description},]
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        return completion.choices[0].message.content

    




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