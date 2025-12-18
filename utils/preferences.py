import json
import os

class UserPreferences:
    """Gerencia preferências do usuário (tema, etc)"""
    
    def __init__(self, prefs_file='user_preferences.json'):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prefs_file = os.path.join(self.base_dir, prefs_file)
        self.prefs = self._load()
    
    def _load(self):
        """Carrega preferências do arquivo JSON"""
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'theme': 'clam'}  # Tema padrão
    
    def save(self):
        """Salva preferências no arquivo JSON"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")
    
    def get_theme(self):
        """Retorna o tema salvo"""
        return self.prefs.get('theme', 'clam')
    
    def set_theme(self, theme):
        """Define e salva o tema"""
        self.prefs['theme'] = theme
        self.save()
