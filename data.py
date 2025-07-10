import os
import sqlite3

#if db doesn't exist here it will create the db using schema commands
if not os.path.isfile("pynote.db"):
    db_con = sqlite3.connect("prototype.db")
    db_cur = db_con.cursor() 
    db_cur.execute("CREATE TABLE NoteReference (OriginalNoteID INTEGER REFERENCES Note (ID), ReferencedNoteID INTEGER REFERENCES Note (ID), BlockNumber INTEGER, PRIMARY KEY (OriginalNoteID, ReferencedNoteID));")
    db_cur.execute("CREATE TABLE Note (ID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR, String TEXT);")
    db_cur.execute("CREATE TABLE sqlite_sequence(name,seq);")
    db_con.commit()
else:
    db_con = sqlite3.connect("pynote.db")
    db_cur = db_con.cursor()

#retrieves the note data with the given id and returns as a dict of data
def retrieve_note_data(id : int):
    
    db_note_data = db_cur.execute("SELECT * FROM Note WHERE ID = (?)", id)
    
    if db_note_data:
        note_dict = {"id" : int(db_note_data[0]), "name" : db_note_data[1], "text" : db_note_data[2]}
    else:
        raise Exception(f"Note data with ID {id} not found.")
    
    return note_dict

def note_in_db(name, text):
    
    existing_notes = db_cur.execute("SELECT * FROM Note WHERE Name = (?) AND String = (?)", (name, text))
    if existing_notes:
        return True
    return False

#inserts the database note data with the given name, text
def insert_note_data(name : str, text : str): 
    
    db_cur.execute("INSERT INTO Note (Name, String) VALUES (?, ?)", (name, text))
    db_con.commit()
    
    return

def update_note_data(id : int, name : str, text : str):
    
    db_cur.execute("UPDATE Note SET Name = (?), String = (?) WHERE ID = (?)", (name, text, id))
    
    db_con.commit()
    
    return

def update_note_reference_data(id : int, referenceid : int, block_number : int):
    
    db_cur.execute("UPDATE NoteReference SET OriginalNoteID = (?), ReferencedNoteID = (?), BlockNumber = (?)", (id, referenceid, block_number))
    
    db_con.commit()