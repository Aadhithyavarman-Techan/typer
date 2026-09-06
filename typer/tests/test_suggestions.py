import pytest
from typer.suggestions import CommandSuggester, SmartTyperApp


class TestCommandSuggesterBasic:
    
    def test_register_single_command(self):
        suggester = CommandSuggester()
        suggester.register_command('greet')
        assert 'greet' in suggester.registered_commands
    
    def test_register_multiple_commands(self):
        suggester = CommandSuggester()
        suggester.register_commands(['greet', 'create', 'delete'])
        assert len(suggester.registered_commands) == 3


class TestCommandSuggesterTypos:
    
    def test_missing_character_typo(self):
        suggester = CommandSuggester()
        suggester.register_commands(['greet', 'create', 'delete', 'update'])
        assert suggester.get_suggestion('gret') == 'greet'
        assert suggester.get_suggestion('crete') == 'create'
    
    def test_extra_character_typo(self):
        suggester = CommandSuggester()
        suggester.register_commands(['greet', 'create', 'delete'])
        assert suggester.get_suggestion('grreeet') == 'greet'
    
    def test_substring_matching(self):
        suggester = CommandSuggester()
        suggester.register_commands(['greet', 'great', 'grant', 'grade'])
        suggestions = suggester.get_suggestions('gre')
        assert len(suggestions) > 0


class TestSmartTyperApp:
    
    def test_register_command(self):
        app = SmartTyperApp()
        
        @app.command('hello')
        def hello_cmd():
            return 'Hello'
        
        assert 'hello' in app.commands
    
    def test_command_not_found_with_suggestion(self):
        app = SmartTyperApp()
        
        @app.command('greet')
        def greet_cmd():
            pass
        
        with pytest.raises(ValueError) as exc_info:
            app.get_command('gret')
        
        assert 'Did you mean' in str(exc_info.value)


class TestRealWorldScenarios:
    
    def test_git_like_commands(self):
        suggester = CommandSuggester()
        suggester.register_commands(['commit', 'push', 'pull', 'clone', 'branch'])
        assert suggester.get_suggestion('committ') == 'commit'
        assert suggester.get_suggestion('pul') == 'pull'
    
    def test_docker_like_commands(self):
        suggester = CommandSuggester()
        suggester.register_commands(['build', 'run', 'stop', 'remove'])
        assert suggester.get_suggestion('bild') == 'build'
    
    def test_npm_like_commands(self):
        suggester = CommandSuggester()
        suggester.register_commands(['install', 'uninstall', 'update'])
        assert suggester.get_suggestion('instal') == 'install'
