import os
import sqlite3

#if db doesn't exist here it will create the db using schema commands
if not os.path.isfile("pynote.db"):
    db_con = sqlite3.connect("prototype.db")
    db_cur = db_con.cursor() 
    db_cur.execute("CREATE TABLE NoteReference (OriginalNoteName VARCHAR REFERENCES Note (Name), ReferencedNoteName VARCHAR REFERENCES Note(Name), BlockNumber INTEGER, PRIMARY KEY (OriginalNoteName, ReferencedNoteName));")
    db_cur.execute("CREATE TABLE Note (Name VARCHAR PRIMARY KEY, String TEXT);")
    db_cur.execute("CREATE TABLE sqlite_sequence(name,seq);")
    db_con.commit()
else:
    db_con = sqlite3.connect("pynote.db")
    db_cur = db_con.cursor()

#retrieves the note data with the given name and returns as a dict of data -- includes name, text and references
def retrieve_note_data(name : str):
    
    note_dict = {}
    
    db_notes = db_cur.execute("SELECT * FROM Note WHERE Name = (?)", (name,))
    db_note_data = db_notes.fetchone()
    if db_note_data:
        
        note_dict.update({"name" : db_note_data[0], "text" : db_note_data[1]})
        
        db_note_references = db_cur.execute("SELECT * FROM NoteReference WHERE OriginalNoteName = (?)", (name,))
        db_note_reference_data = db_note_references.fetchall()
        reference_dict = {}
        for reference in db_note_reference_data:
            
            #reference[1] -- referenced note name, reference[2] -- block number
            reference_dict.update({reference[1] : int(reference[2])})
        
        note_dict.update({"references" : reference_dict})
        
    else:
        raise Exception(f"Note data with name: {name} not found.")
    
    return note_dict

def retrieve_all_note_data():
    
    db_note_names = db_cur.execute("SELECT Name FROM Note")
    note_names = db_note_names.fetchall()
    
    return [retrieve_note_data(name[0]) for name in note_names]

#checks for if note with given name is in the database
def note_in_db(name):
    
    existing_notes = db_cur.execute("SELECT * FROM Note WHERE Name = (?)", (name,))
    if existing_notes.fetchall():
        return True
    return False

def reference_in_db(note_name, reference_name, block_number):
    
    existing_references = db_cur.execute("SELECT * FROM NoteReference WHERE OriginalNoteName = (?) AND ReferencedNoteName = (?) AND BlockNumber = (?)", (note_name, reference_name, block_number))
    if existing_references.fetchall():
        return True
    return False

#inserts the database note data with the given name, text
def insert_note_data(name : str, text : str): 
    
    db_cur.execute("INSERT INTO Note (Name, String) VALUES (?, ?)", (name, text))
    db_con.commit()
    
    return

def insert_note_reference_data(note_name : str, reference_name : str, block_number : int):
    
    db_cur.execute("INSERT INTO NoteReference (OriginalNoteName, ReferencedNoteName, BlockNumber)", (note_name, reference_name, block_number))
    db_con.commit()

def update_note_data(old_name : str, new_name : str, text : str):
    
    db_cur.execute("UPDATE Note SET Name = (?), String = (?) WHERE Name = (?)", (new_name, text, old_name))
    
    db_con.commit()
    
    return

def update_note_reference_data(name : str, reference_name : str, block_number : int):
    
    db_cur.execute("UPDATE NoteReference SET OriginalNoteName = (?), ReferencedNoteName = (?), BlockNumber = (?) WHERE Name = (?)", (name, reference_name, block_number, name))
    db_con.commit()
    
#empties database
def CLEAR_TABLE(table_name : str = ""):
    
    
    if table_name: 
        if table_name.lower() == "note":
            table == "Note"
        elif table_name.lower() == "notereference":
            table == "NoteReference"
        else:
            raise Exception(f"Table name: {table_name} invalid")
        if input(f"Are you sure you want to delete all entries from {table}? (y/n) ").lower() == "y":
            print(f"Deleting entries from {table} table...")
            db_cur.execute("DELETE FROM (?)", (table,))
        else:
            return
    else:
        if input(f"Are you sure you want to delete all entries from all tables in pynote.db? (y/n) ").lower() == "y":
            print(f"Deleting entries from all tables in pynote.db...")
            db_cur.execute("DELETE FROM Note")
            db_cur.execute("DELETE FROM NoteReference")
        else:
            return
    
    db_con.commit()
    