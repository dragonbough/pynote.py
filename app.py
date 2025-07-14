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
        
        original_name = self.original_name if self.original_name else self.name
        
        #if the original name of the note is not present in the DB, just insert this version 
        if not data.note_in_db(original_name):
            data.insert_note_data(self.name, self.text)
        #if the original name of the note is present in the DB just update the name and text to be what it is now 
        else:    
            data.update_note_data(original_name, self.name, self.text)
        
        #for each reference in this note just update entries in DB, or if not in DB, insert them 
        for reference_name in list(self.references.keys()):
            
            if data.reference_in_db(self.name, reference_name):
                data.update_note_reference_data(self.name, reference_name, self.references[reference_name])
            else:
                data.insert_note_reference_data(self.name, reference_name, self.references[reference_name])
            
    def reference_note(self, referenced_note_name : str, block_number : int):
        #block number refers to the specific word index that the link was addded to
        self.references.update({referenced_note_name : block_number})

#stores the current user notes
class UserNotes():
    
    #static method that returns a UserNotes object of all the user notes
    @staticmethod
    def get_all_notes():
        
        notes = []
        for note_data in data.retrieve_all_note_data():
            notes.append(Note(note_data["name"], note_data["text"], note_data["references"]))
        return UserNotes(notes)
    
    def __init__(self, notes : list[Note] = []):
        
        self._notes = notes
    
    def get(self, note_name : str = None):
        
        #you can get the note via name, or just all of them if no name is inputted
        if note_name:
            if note_name in [note.name for note in self._notes]:
                return [note for note in self._notes if note.name == note_name][0]
          
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
            
            
user_notes = UserNotes.get_all_notes()
note1 = user_notes.get("note no.0 is now updated")
note2 = user_notes.get("note no.4 is now updated")
note1.reference_note(note2.name, 1)
