from typing import Optional, List, Dict, Tuple
from difflib import get_close_matches, SequenceMatcher


class CommandSuggester:
    
    def __init__(self, threshold: float = 0.6, max_suggestions: int = 3):
        self.threshold = threshold
        self.max_suggestions = max_suggestions
        self.registered_commands: List[str] = []
        self.command_aliases: Dict[str, List[str]] = {}
    
    def register_command(self, name: str, aliases: List[str] = None) -> None:
        if name not in self.registered_commands:
            self.registered_commands.append(name)
        
        if aliases:
            self.command_aliases[name] = aliases
            for alias in aliases:
                if alias not in self.registered_commands:
                    self.registered_commands.append(alias)
    
    def register_commands(self, names: List[str]) -> None:
        for name in names:
            self.register_command(name)
    
    def detect_typo_type(self, typo: str, suggestion: str) -> str:
        if len(typo) > len(suggestion):
            return "extra_character"
        elif len(typo) < len(suggestion):
            return "missing_character"
        elif typo.lower() == suggestion.lower():
            return "case_mismatch"
        else:
            return "typo"
    
    def get_suggestions(self, typo: str) -> List[str]:
        if not self.registered_commands:
            return []
        
        typo_lower = typo.lower()
        results = []
        
        for cmd in self.registered_commands:
            cmd_lower = cmd.lower()
            if cmd_lower == typo_lower:
                results.append((cmd, 1.0))
                continue
            
            if typo_lower in cmd_lower or cmd_lower in typo_lower:
                ratio = SequenceMatcher(None, typo_lower, cmd_lower).ratio()
                if ratio >= self.threshold:
                    results.append((cmd, ratio))
        
        if not results:
            matches = get_close_matches(
                typo,
                self.registered_commands,
                n=self.max_suggestions * 2,
                cutoff=self.threshold
            )
            for match in matches:
                ratio = SequenceMatcher(None, typo.lower(), match.lower()).ratio()
                results.append((match, ratio))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, _ in results[:self.max_suggestions]]
    
    def get_suggestion(self, typo: str) -> Optional[str]:
        suggestions = self.get_suggestions(typo)
        return suggestions[0] if suggestions else None
    
    def get_suggestions_with_confidence(self, typo: str) -> List[Tuple[str, float]]:
        if not self.registered_commands:
            return []
        
        typo_lower = typo.lower()
        results = []
        
        for cmd in self.registered_commands:
            cmd_lower = cmd.lower()
            ratio = SequenceMatcher(None, typo_lower, cmd_lower).ratio()
            
            if ratio >= self.threshold:
                results.append((cmd, ratio))
        
        if not results:
            matches = get_close_matches(
                typo,
                self.registered_commands,
                n=self.max_suggestions * 2,
                cutoff=self.threshold
            )
            for match in matches:
                ratio = SequenceMatcher(None, typo.lower(), match.lower()).ratio()
                results.append((match, ratio))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:self.max_suggestions]
    
    def format_suggestion_message(self, typo: str, suggestion: str) -> str:
        return f"No such command: '{typo}'. Did you mean '{suggestion}'?"
    
    def format_multiple_suggestions_message(self, typo: str, suggestions: List[str]) -> str:
        if not suggestions:
            return f"No such command: '{typo}'"
        
        if len(suggestions) == 1:
            return self.format_suggestion_message(typo, suggestions[0])
        
        suggestions_str = "', '".join(suggestions)
        return f"No such command: '{typo}'. Did you mean one of: '{suggestions_str}'?"
    
    def is_similar(self, cmd1: str, cmd2: str) -> bool:
        matches = get_close_matches(
            cmd1,
            [cmd2],
            n=1,
            cutoff=self.threshold
        )
        return bool(matches)
    
    def find_close_matches(self, typo: str) -> List[str]:
        return get_close_matches(
            typo,
            self.registered_commands,
            n=self.max_suggestions,
            cutoff=self.threshold
        )
    
    def similarity_score(self, str1: str, str2: str) -> float:
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


class SmartTyperApp:
    
    def __init__(self, name: str = "app", help: str = ""):
        self.name = name
        self.help = help
        self.commands: Dict[str, callable] = {}
        self.suggester = CommandSuggester()
        self.command_help: Dict[str, str] = {}
    
    def command(self, name: str = None, aliases: List[str] = None):
        def decorator(func):
            cmd_name = name or func.__name__
            self.commands[cmd_name] = func
            self.suggester.register_command(cmd_name, aliases)
            
            if func.__doc__:
                self.command_help[cmd_name] = func.__doc__.strip()
            
            return func
        return decorator
    
    def get_command(self, name: str):
        if name in self.commands:
            return self.commands[name]
        
        suggestions = self.suggester.get_suggestions(name)
        
        if suggestions:
            if len(suggestions) == 1:
                message = self.suggester.format_suggestion_message(name, suggestions[0])
            else:
                message = self.suggester.format_multiple_suggestions_message(name, suggestions)
            raise ValueError(message)
        else:
            raise ValueError(f"No such command: '{name}'")
    
    def list_commands(self) -> List[str]:
        return list(self.commands.keys())
    
    def get_command_help(self, name: str) -> Optional[str]:
        return self.command_help.get(name)
    
    def find_similar_commands(self, partial_name: str) -> List[str]:
        return self.suggester.find_close_matches(partial_name)
