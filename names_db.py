
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
    
    def add(self, linkedin_id, name):
        self._dict[linkedin_id] = name
        self.write_dictionary()
    
    def get(self, linkedin_id):
        return self._dict.get(linkedin_id, None)
    
