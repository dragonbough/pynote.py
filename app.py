import data
import numpy

class Note():
    
    def __init__(self, id : int = None, name : str = None, text : str = None):
        
        self.id = id
        self.name = name
        self.text = text
        self.references = {}
        
        #if id passed into Note construcutor -- it will update note with data from DB
        #if only name and text passed into Note constructor -- it will create entry in DB with this note        
        if self.id:
            note_data = data.retrieve_note_data(self.id)
            self.name = note_data["name"]
            self.text = note_data["text"]
        elif self.name and self.text:
            data.insert_note_data(name=self.name, text=self.text)
        else:
            raise Exception("Note initialised with insufficient arguments")
    
    def update_data(self):
        data.update_note_data(self.id, self.name, self.text)
    
    def reference_note(self, referenced_note, block_number : int):
        #block number refers to the specific word index that the link was addded to
        self.references.update({referenced_note : block_number})
        data.update_note_reference_data(self.id, referenced_note.id, block_number)

#stores the current user notes
class UserNotes():
    
    def __init__(self, notes : list[Note] = []):
        
        self._notes = []
    
    def get(self):
        
        return self._notes
    
    def add(self, notes : Note | list[Note]):
        
        if type(notes) == list:
            self._notes.extend(notes)
        elif type(notes) == Note:
            self._notes.append(notes)
            
class NoteNetwork():
    
    def __init__(self, user_notes : UserNotes):
        
        pass
        # self.notes = user_notes.get()
        # matrix = []
        # for note in self.notes:
        #     for note in self.notes:
        #         matrix +
        # self.matrix = numpy.matrix([ [ [0] for note in self.notes ] for note in self.notes ])
        # print(self.matrix)
        
        
        
# user_notes = UserNotes()
# notes = [Note(i) for i in range(10)]
# user_notes.add(notes)
# network = NoteNetwork(user_notes)