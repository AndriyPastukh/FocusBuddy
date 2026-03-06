class LookupsManager:
    def __init__(self, api):
        self.api = api
        self.categories = []
        self.priorities = []
        self.statuses = []
        self.difficulties = []
        
        # Load immediately
        self.load_all()

    def load_all(self):
        """Fetch all lookup data from the backend."""
        # 1. Main Lookups (Categories, Priorities, Statuses)
        try:
            if hasattr(self.api, 'get_lookups'):
                data = self.api.get_lookups()
            else:
                data = self.api._run(["--getLookups"])
                
            if isinstance(data, dict):
                self.categories = data.get('categories', [])
                self.priorities = data.get('priorities', [])
                self.statuses = data.get('statuses', [])
            else:
                self.categories = []
                self.priorities = []
                self.statuses = []
                
        except Exception as e:
            print(f"Error loading lookups: {e}")
            self.categories = []
            self.priorities = []
            self.statuses = []

        # 2. Difficulties (for Habits)
        try:
            if hasattr(self.api, 'get_difficulties'):
                self.difficulties = self.api.get_difficulties()
            else:
                self.difficulties = self.api._run(["--getDifficulties"])
                if not isinstance(self.difficulties, list): 
                    self.difficulties = []
        except:
            self.difficulties = []

    def get_category_color(self, cat_id):
        for c in self.categories:
            if str(c['id']) == str(cat_id):
                return c.get('color', '#FFFFFF')
        return '#FFFFFF'

    def get_priority_color(self, prio_id):
        for p in self.priorities:
            if str(p['id']) == str(prio_id):
                return p.get('color', '#000000')
        return '#000000'