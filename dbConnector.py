import sqlite3
from datetime import datetime



class CaseDatabase:
    def __init__(self, database_name):
        self.database_name = database_name
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.database_name)

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_files_table(self):
        self.connect()
        cursor = self.conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS dir_parse (
        file_id INTEGER PRIMARY KEY NOT NULL,
        file_path TEXT,
        file_hash TEXT,
        file_modified TIMESTAMP,
        file_access TIMESTAMP,
        file_creation TIMESTAMP
        );
        """

        cursor.execute(create_table_query)
        self.conn.commit()
        self.conn.close()

    def create_cases_table(self):
        self.connect()
        cursor = self.conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS cases (
            case_name TEXT NOT NULL,
            case_path TEXT NOT NULL,
            case_description TEXT,
            investigator_name TEXT,
            investigator_info TEXT,
            created_at TIMESTAMP
        );
        """

        cursor.execute(create_table_query)
        self.conn.commit()
        self.disconnect()

    def insert_dir(self, dir_data):
        self.connect()
        cursor = self.conn.cursor()

        file_path = dir_data['file_path']
        file_hash = dir_data['file_hash']
        file_modified = dir_data['file_modified']
        file_access = dir_data['file_access']
        file_creation = dir_data['file_creation']

        insert_query = """
        INSERT INTO dir_parse (
            file_path, 
            file_hash, 
            file_modified, 
            file_access, 
            file_creation)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(insert_query, (
            file_path,
            file_hash,
            file_modified,
            file_access,
            file_creation
        ))
        
        self.conn.commit()
        self.disconnect()
        
        

    def insert_case(self, case_data):
        self.connect()
        cursor = self.conn.cursor()

        case_name = case_data['case_name']
        case_path = case_data['case_path']
        case_description = case_data['case_description']
        investigator_name = case_data['investigator_name']
        investigator_info = case_data['investigator_info']
        created_at = datetime.now()

        insert_query = """
        INSERT INTO cases (
            case_name,
            case_path,
            case_description,
            investigator_name,
            investigator_info,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?);
        """

        cursor.execute(insert_query, (
            case_name,
            case_path,
            case_description,
            investigator_name,
            investigator_info,
            created_at
        ))

        self.conn.commit()
        self.disconnect()
