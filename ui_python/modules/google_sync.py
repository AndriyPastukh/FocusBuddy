

import os
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build

class GoogleSyncService:
    def __init__(self, backend_connector):
        self.connector = backend_connector

    def sync_tasks(self):
        print("Connecting to Google Tasks API...")
        google_tasks = [
            {"title": "Buy milk", "id": "g1"},
            {"title": "Finish Coursework", "id": "g2"}
        ]
        
        for task in google_tasks:
            print(f"Syncing: {task['title']}")
            # Передаємо в C++ Core
            self.connector.run(["--syncGoogle", task['title'], task['id']])
            
        print("Sync Complete!")