import sublime, sublime_plugin
import json, re, sys, threading

from .util.completion_source import CompletionSource

def build_textSet(view):
    result = set()
    for region in view.sel():
        text = view.substr(region)

        if text:         
            result = result.union(re.sub(r'\s','',text))
            
    return result

textSetCompletionSource = CompletionSource()
class SelectionBinaryInversionViewEventListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        textSetCompletionSource.reset()
        textSetCompletionSource.set_result(build_textSet(view))

    def on_selection_modified_async(self, view):
        textSetCompletionSource.reset()
        textSetCompletionSource.set_result(build_textSet(view))


class SelectionBinaryInversionCommand(sublime_plugin.TextCommand):
    def __init__(self, args):
        sublime_plugin.TextCommand.__init__(self, args)
        self.menu = None

    def run(self, edit):
        for region in self.view.sel():
            self.inverse_region(edit, region)

    def is_enabled(self):
        self.textSet = textSetCompletionSource.get_result()
        return len(self.textSet) == 2 if self.textSet else False;

    def inverse_region(self, edit, region):
        text = self.view.substr(region)
        self.view.replace(edit, region, 
            ''.join([
                self.textSet.difference(text[i]).pop()
                if text[i] in self.textSet else text[i] 
                for i in range(len(text))
            ]))

    def description(self):
        caption = self.get_menu_item('bin_inv')['$caption']
        return caption + ' ( ' + ' <-> '.join(self.textSet) + ' )' if self.is_enabled() else caption

    def get_menu_item(self, item_id):
        if not self.menu:
            self.menu = json.loads(sublime.load_resource('Packages/User/Context.sublime-menu'))[0]['children']

        for item in self.menu:
            if item['id'] == item_id:
                return item
        return None