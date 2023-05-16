
import pickle

class NamesDB:
    def __init__(self, file_path):
        self.file_path = file_path
        self._dict = self.read_dictionary()


    def __repr__(self):
        return f"file_path = {self.file_path}\n" +  repr(self._dict)
    

     
    def __contains__(self, item):
        if item in self._dict:
            return True
        else:
            return False
        
    def __getitem__(self, item):
         return self._dict[item]
    
    def read_dictionary(self):
        try:
            with open(self.file_path, 'rb+') as file:
                dictionary = pickle.load(file)
                return dictionary
        except FileNotFoundError:
            print(f"File '{self.file_path}' not found.")
            return {}
        

    def write_dictionary(self):
        with open(self.file_path, 'wb+') as file:
            pickle.dump(self._dict, file)
    

class Entry():
    def __init__(self, linkedin_id, name, a_tag, status, date_updated):
        self.linkedin_id = linkedin_id
        self.name = name
        self.a_tag = a_tag
        self.status = status
        self.date_updated = date_updated
    
    def __repr__(self):
        return f"linkedin_id = {self.linkedin_id}\n" + \
            f"name = {self.name}\n" + \
            f"a_tag = {self.a_tag}\n" + \
            f"status = {self.status}\n" + \
            f"date_updated = {self.date_updated}\n"
    
    def __str__(self):
        return f"linkedin_id = {self.linkedin_id}\n" + \
            f"name = {self.name}\n" + \
            f"a_tag = {self.a_tag}\n" + \
            f"status = {self.status}\n" + \
            f"date_updated = {self.date_updated}\n"