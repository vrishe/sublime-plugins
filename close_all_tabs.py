import sublime, sublime_plugin

class CloseAllTabsCommand(sublime_plugin.WindowCommand):
    def run(self):
        for view in self.window.views():
            self.window.focus_view(view)
            self.window.run_command("close_file")