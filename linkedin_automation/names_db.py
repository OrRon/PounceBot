
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
    
    def __setitem__(self, k, v):
         self._dict[k] = v
         self.write_dictionary()
    
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