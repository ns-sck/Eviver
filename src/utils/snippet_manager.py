import json
import os

class SnippetManager:
    def __init__(self):
        self.snippets = {}
        self.load_snippets()

    def load_snippets(self):
        try:
            snippet_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'snippets.json')
            with open(snippet_file, 'r') as f:
                self.snippets = json.load(f)
        except Exception as e:
            print(f"Error loading snippets: {e}")
            self.snippets = {}

    def get_snippet(self, prefix):
        """Get a snippet by its prefix"""
        if prefix in self.snippets:
            return self.snippets[prefix]
        return None

    def get_all_prefixes(self):
        """Get all available snippet prefixes"""
        return list(self.snippets.keys())

    def get_snippet_body(self, prefix):
        """Get the body of a snippet by its prefix"""
        snippet = self.get_snippet(prefix)
        if snippet and 'body' in snippet:
            return '\n'.join(snippet['body'])
        return None 