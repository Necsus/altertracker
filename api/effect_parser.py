import re
from typing import List, Dict, Optional, Tuple

class EffectParser:
    def __init__(self):
        # Patterns pour les sous-conditions qui créent des effets séparés
        self.subcondition_patterns = [
            # Français
            r'(.+?)\.\s+(Sur\s+\d+\+):\s*(.+)',           # "Lancez un dé. Sur 4+: action"
            r'(.+?)\.\s+(Si\s+vous\s+le\s+faites):\s*(.+)', # "Action. Si vous le faites: action"
            r'(.+?),\s+(sinon\s+.+)',                       # "Action, sinon action"
            # Anglais
            r'(.+?)\.\s+(On\s+a\s+\d+\+):\s*(.+)',        # "Roll a die. On a 4+: action"
            r'(.+?)\.\s+(If\s+you\s+do):\s*(.+)',         # "Action. If you do: action"
            r'(.+?),\s+(otherwise\s+.+)',                   # "Action, otherwise action"
        ]
        
        # Patterns pour détecter les lignes principales (double espace)
        self.line_separators = [
            r'(?<=\.)\s\s+(?=\{[JHR]\})',      # Double+ espace après point, puis coût
            r'(?<=\.)\s\s+(?=Lorsque\s)',      # Double+ espace après point, puis "Lorsque"
            r'(?<=\.)\s\s+(?=When\s)',         # Double+ espace après point, puis "When"
            r'(?<=\.)\s\s+(?=À\s)',            # Double+ espace après point, puis "À"
            r'(?<=\.)\s\s+(?=At\s)',           # Double+ espace après point, puis "At"
            r'(?<=\.)\s\s+(?=\[\])',           # Double+ espace après point, puis "[]"
        ]
    
    def parse_to_minimal_json(self, effect_text: str, language: str = "auto") -> List[Dict]:
        """Parse le texte d'effet et retourne un JSON minimal pour requêtage"""
        if not effect_text:
            return []
        
        # Détection automatique de la langue si non spécifiée
        if language == "auto":
            language = self._detect_language(effect_text)
        
        # Parse les effets
        return self._parse_effect_text(effect_text, language)
    
    def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        french_keywords = ['vous', 'je', 'si', 'lorsque', 'gagne', 'carte', 'piochez']
        english_keywords = ['you', 'may', 'if', 'when', 'gain', 'card', 'draw']
        
        french_count = sum(1 for word in french_keywords if word.lower() in text.lower())
        english_count = sum(1 for word in english_keywords if word.lower() in text.lower())
        
        return "fr" if french_count > english_count else "en"
    
    def _parse_effect_text(self, effect_text: str, language: str) -> List[Dict]:
        """Parse le texte d'effet complet et retourne les effets parsés"""
        # Sépare les lignes d'effet principales
        main_lines = self._split_effect_lines(effect_text)
        
        all_parsed_effects = []
        
        for main_line in main_lines:
            # Parse la ligne principale
            base_effect = self._parse_single_line(main_line.strip(), language)
            
            # Vérifier s'il y a des sous-effets à séparer
            sub_effects = self._extract_sub_effects(base_effect, language)
            
            # Ajouter tous les effets
            all_parsed_effects.extend(sub_effects)
        
        return all_parsed_effects
    
    def _split_effect_lines(self, text: str) -> List[str]:
        """Sépare les lignes d'effet principales"""
        lines = [text]
        for separator in self.line_separators:
            new_lines = []
            for line in lines:
                new_lines.extend(re.split(separator, line))
            lines = new_lines
        
        return [line.strip() for line in lines if line.strip()]
    
    def _extract_sub_effects(self, base_effect: Dict, language: str) -> List[Dict]:
        """Sépare les effets complexes en sous-effets"""
        action_text = base_effect.get('action_text', '')
        
        # Chercher les patterns de sous-conditions
        for pattern in self.subcondition_patterns:
            match = re.search(pattern, action_text)
            if match:
                return self._split_complex_effect(base_effect, match)
        
        # Pas de sous-effet, retourner l'effet original
        return [base_effect]
    
    def _split_complex_effect(self, base_effect: Dict, match) -> List[Dict]:
        """Sépare un effet complexe en plusieurs effets"""
        primary_action = match.group(1).strip()
        subcondition = match.group(2).strip()
        conditional_action = match.group(3).strip()
        
        effects = []
        
        # Effet 1: Action principale
        effect1 = base_effect.copy()
        effect1['action_text'] = primary_action
        effects.append(effect1)
        
        # Effet 2: Effet conditionnel
        effect2 = {
            'trigger_text': None,
            'condition_text': subcondition,
            'action_text': conditional_action,
            'trigger_type': 'dependent',
            'cost_type': None,
        }
        effects.append(effect2)
        
        return effects
    
    def _parse_single_line(self, line: str, language: str) -> Dict:
        """Parse une seule ligne selon [déclenchement][condition][action]"""
        result = {
            'trigger_text': None,
            'condition_text': None,
            'action_text': None,
            'trigger_type': None,
            'cost_type': None,
        }
        
        # Étape 1: Vérifier si pas de déclenchement (commence par [])
        if line.startswith('[]'):
            remaining_text = line[2:].strip()
        else:
            trigger_info, remaining_text = self._extract_trigger(line, language)
            if trigger_info:
                result.update(trigger_info)
            else:
                remaining_text = line
        
        # Étape 2: Chercher [] pour absence de condition
        if remaining_text.startswith('[]'):
            action_text = remaining_text[2:].strip()
        else:
            condition_text, action_text = self._extract_condition(remaining_text, language)
            result['condition_text'] = condition_text
        
        # Étape 3: Le reste est l'action
        result['action_text'] = action_text.strip() if action_text else remaining_text.strip()
        
        return result
    
    def _extract_trigger(self, line: str, language: str) -> Tuple[Optional[Dict], str]:
        """Extrait le déclenchement du début de ligne"""
        
        # Coût d'activation {J}, {H}, {R}
        match = re.match(r'^\{([JHR])\}\s*', line)
        if match:
            cost = match.group(1)
            remaining = line[match.end():]
            return {
                'trigger_text': f'{{{cost}}}',
                'trigger_type': 'activation_cost',
                'cost_type': cost,
            }, remaining
        
        if language == "fr":
            # Français
            # When events avec —
            match = re.match(r'^Lorsque\s+(.+?)\s+—\s*', line)
            if match:
                event = match.group(1)
                remaining = line[match.end():]
                return {
                    'trigger_text': f"Lorsque {event}",
                    'trigger_type': 'when_event',
                }, remaining
            
            # At time avec —
            match = re.match(r'^À\s+(Crépuscule|Midi|Aube)\s+—\s*', line)
            if match:
                time = match.group(1)
                remaining = line[match.end():]
                return {
                    'trigger_text': f"À {time}",
                    'trigger_type': 'at_time',
                }, remaining
        else:
            # Anglais
            # When events avec —
            match = re.match(r'^When\s+(.+?)\s+—\s*', line)
            if match:
                event = match.group(1)
                remaining = line[match.end():]
                return {
                    'trigger_text': f"When {event}",
                    'trigger_type': 'when_event',
                }, remaining
            
            # At time avec —
            match = re.match(r'^At\s+(Dusk|Noon|Dawn)\s+—\s*', line)
            if match:
                time = match.group(1)
                remaining = line[match.end():]
                return {
                    'trigger_text': f"At {time}",
                    'trigger_type': 'at_time',
                }, remaining
        
        return None, line
    
    def _extract_condition(self, text: str, language: str) -> Tuple[Optional[str], str]:
        """Extrait la condition du texte"""
        
        if language == "fr":
            # Conditions françaises
            patterns = [
                r'^(Si\s+.+?):\s*',
                r'^(Sauf\s+si\s+.+?):\s*',
                r'^(À\s+moins\s+que\s+.+?):\s*'
            ]
        else:
            # Conditions anglaises
            patterns = [
                r'^(If\s+.+?):\s*',
                r'^(Unless\s+.+?):\s*'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                condition = match.group(1)
                action_text = text[match.end():]
                return condition, action_text
        
        return None, text