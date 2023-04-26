import sublime
import sublime_plugin
import os, sys

def product(a, b):
  for first in a:
    for second in b:
      yield os.path.normpath(os.path.join(first, second))

class ReadonlyViewLoadListener(sublime_plugin.EventListener):
  def on_load(self, view):
    subfolders = view.settings().get('readonly.subfolders')
    filename = view.file_name()
    print(filename)
    if not subfolders: return
    for prefix in product(view.window().folders(), subfolders):
      if filename.startswith(prefix):
        view.set_read_only(True)
        view.set_status('readonly.status', 'readonly')
        view.window().status_message("View {} is readonly.".format(filename))
        return

class ReadonlyDisableCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.set_read_only(False)
    self.view.erase_status('readonly.status')
    self.view.window().status_message("View {} is writeable.".format(filename))

  def is_visible(self):
      return self.view.is_read_only() and self.view.get_status('readonly.status') == 'readonly'
