import sublime, sublime_plugin
import json, re, string, sys

from collections import deque
from .util.completion_source import CompletionSource

def build_shiftVector(view):
    result = None
    for region in view.sel():
        text = view.substr(region)
        vector = (list(), deque())

        for i, c in enumerate(text):
            if not c in string.whitespace:
                vector[0].append(i)
                vector[1].append(c)
            elif c == '\n':
                return None

        if not result:
            result = []
        result.append(vector)

    return result

shiftVectorCompletionSource = CompletionSource()
class SelectionRotaryShiftViewEventListener(sublime_plugin.EventListener):   
    def on_activated_async(self, view):
        shiftVectorCompletionSource.reset()
        shiftVectorCompletionSource.set_result(build_shiftVector(view))      

    def on_selection_modified_async(self, view):
        shiftVectorCompletionSource.reset()
        shiftVectorCompletionSource.set_result(build_shiftVector(view))


class SelectionRotaryShiftCommand(sublime_plugin.TextCommand):
    def __init__(self, args):
        sublime_plugin.TextCommand.__init__(self, args)
        self.menu = None

    def run(self, edit, direction):
        for i, region in enumerate(self.view.sel()):
            self.shift_region(edit, region, direction, i)

    def is_enabled(self):
        self.shiftVector = shiftVectorCompletionSource.get_result()
        return len(self.shiftVector[0]) >= 2 if self.shiftVector else False;

    def shift_region(self, edit, region, direction, idx):
        text = list(self.view.substr(region))
        vector = self.shiftVector[idx]

        vector[1].rotate(direction)
        for i, j in enumerate(vector[0]):
            text[j] = vector[1][i]

        self.view.replace(edit, region, ''.join(text))

    def get_menu_item(self, item_id):
        if not self.menu:
            self.menu = json.loads(sublime.load_resource('Packages/User/Context.sublime-menu'))[0]['children']

        for item in self.menu:
            if item['id'] == item_id:
                return item
        return None