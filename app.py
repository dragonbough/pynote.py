import data
import numpy

class Note():

    #factory method -- gives you the note you want from DB
    @staticmethod
    def get_note(name : str):
        
        #checks if the note name is already in DB
        #if so, then retrieve the note data from DB
        if data.note_in_db(name):
            note_data = data.retrieve_note_data(name)
            note_name = note_data["name"]
            note_text = note_data["text"]
            note_references = note_data["references"]
            print(f"retrieved note -- name: {note_name}, text: {note_text}, references: {note_references}")
            return Note(note_name, note_text, note_references)
        else:
            raise Exception(f"Note named: {name} does not exist in DB")

    
    def __init__(self, name : str, text : str = "", references : dict = {}):
        
        self.id = None
        self.original_name = None
        self.name = name
        self.text = text
        self.references = references
    
    #updates name but doesn't update DB yet -- must keep reference of original name
    def update_name(self, new_name):
        
        if not self.original_name:
            self.original_name = self.name
        self.name = new_name
    
    #solidifies database update -- if not in database already, inserted. if already in database, update database entry
    def update_database(self):
        
        if not data.note_in_db(self.name):
            data.insert_note_data(self.name, self.text)
        else:    
            data.update_note_data(self.original_name, self.name, self.text)
        
        for reference_name in list(self.references.keys()):
            data.update_note_reference_data(self.name, reference_name, self.references[reference_name])
            
    def reference_note(self, referenced_note_name : str, block_number : int):
        #block number refers to the specific word index that the link was addded to
        self.references.update({referenced_note_name : block_number})

#stores the current user notes
class UserNotes():
    
    def __init__(self, notes : list[Note] = []):
        
        self._notes = notes
    
    def get(self, note_name : str = None):
        
        #you can get the note via name, or just all of them if no name is inputted
        if note_name in [note.name for note in self._notes]:
            return [note.name for note in self._notes if note.name == note_name][0]
          
        return self._notes
    
    def add(self, notes : Note | list[Note]):
        
        if type(notes) == list:
            self._notes.extend(notes)
        elif type(notes) == Note:
            self._notes.append(notes)
    
    def update_notes(self, note_names : list[str] = None):
        
        #if no specific note_names are entered, just updates all of them
        if note_names == None:
            [note.update_database() for note in self._notes]
        else:
            [note.update_database() for note in self._notes if note.name in note_names]
            
            
#network graph representation of each note
class NoteNetwork():
    
    def __init__(self, notes : UserNotes):
        
        pass
        
# user_notes = UserNotes()
# for i in range (10):
#     note = Note.get_note(f"note no.{i}")
#     user_notes.add(note)

# print([note.name for note in user_notes.get()])
 
# for note in user_notes.get():
#     note.update_name(f"{note.name} is now updated")   
    
# user_notes.update_notes()
