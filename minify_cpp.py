import sublime
import sublime_plugin
import sys

from .util.anonymous_object import AnonymousObject

# class LoggingEventListener(sublime_plugin.EventListener):
#   def on_activated_async(self, view):
#     self.last=-1
#     self.class_names = {v:k for k,v in sys.modules['sublime'].__dict__.items() if k.startswith('CLASS_')}
#     print(self.class_names)
#     self.on_selection_modified_async(view)

#   def on_selection_modified_async(self, view):
#     for r in [r for r in view.sel() if r.empty() and r.a != self.last]:
#       print('{0} '.format(repr(view.substr(r.a))).replace('\n','\\n') + self.flags_to_string(view.classify(r.a)))
#       self.last=r.a

#   def flags_to_string(self, value):
#     names=[]
#     for i in range(64):
#       flag = 1<<i
#       if value&flag:
#         names.append(self.class_names.get(flag, "<unknown> [{0}]".format(flag)))
#     return "{0}: ".format(value) + str.join(' | ', names)

class MinifyCppCommand(sublime_plugin.TextCommand):
  def clone_view(self):
    v = self.view.window().new_file()
    v.set_name('Minify Results')
    v.set_scratch(True)
    v.settings().set('word_wrap', self.view.settings().get('word_wrap'))
    v.assign_syntax(self.view.settings().get('syntax'))
    return v

  def run(self, edit):
    v = self.view
    text_len = v.size()
    text_region = sublime.Region(0, text_len)

    segments = []
    text_region_active = text_region
    def append_segment(pos, count = 1):
      nonlocal text_region_active
      new_region = sublime.Region(text_region_active.a, pos)
      text_region_active = sublime.Region(pos + count, text_region_active.b)
      if not new_region.empty():
        segments.append(new_region)

    comment_start = -1
    is_sl_comment = False
    is_ml_comment = False
    is_pragma = False

    cur  = AnonymousObject({'char': '', 'cls': 0, 'i': -1})
    prev = AnonymousObject({'char': '', 'cls': 0, 'i': -1})
    for i in range(text_len):
      cur.char = v.substr(i)
      cur.cls = v.classify(i)
      cur.i = i

      if prev.cls & sublime.CLASS_PUNCTUATION_START and cur.cls == 0\
          and prev.char == '/' and cur.char == '/':
        is_sl_comment = not is_ml_comment
        if is_sl_comment:
          comment_start = prev.i
      if prev.cls & sublime.CLASS_PUNCTUATION_START and cur.cls == 0\
          and prev.char == '/' and cur.char == '*':
        is_ml_comment = not is_sl_comment
        if is_ml_comment:
          comment_start = prev.i
      if cur.cls & sublime.CLASS_LINE_START and cur.char == '#':
        is_pragma = True

      def check_point():
        erase_point = False
        erase_point |= prev.cls & sublime.CLASS_WORD_END and cur.cls & sublime.CLASS_PUNCTUATION_START 

        if erase_point:
          append_segment(prev.i)
          return

        erase_point |= cur.cls & sublime.CLASS_EMPTY_LINE
        erase_point |= cur.cls in [0, sublime.CLASS_LINE_START] and cur.char.isspace()
        erase_point |= not is_pragma and cur.cls & sublime.CLASS_LINE_END
        erase_point |= cur.cls & sublime.CLASS_PUNCTUATION_END and not (\
          cur.cls & sublime.CLASS_WORD_START or is_pragma and cur.cls & sublime.CLASS_LINE_END)

        if erase_point:
          append_segment(cur.i)

      if not is_sl_comment and not is_ml_comment:
        check_point()

      if is_sl_comment and cur.cls & sublime.CLASS_LINE_END:
        is_sl_comment = False
        append_segment(comment_start, cur.i - comment_start + 1)
      if is_ml_comment and cur.cls == 0\
          and prev.char == '*' and cur.char == '/':
        is_ml_comment = False
        append_segment(comment_start, cur.i - comment_start + 1)
      if is_pragma and cur.cls & sublime.CLASS_LINE_END:
        is_pragma = False;

      cur, prev = prev, cur

    if not is_ml_comment and not text_region_active.empty():
      segments.append(text_region_active)

    new_text = ''.join([v.substr(r) for r in segments])

    results_view = self.clone_view()
    results_view.run_command(
        'append',
        {'characters': new_text, 'force': True, 'scroll_to_end': False}
    )

  def is_visible(self):
    syntax = self.view.settings().get('syntax')
    print(syntax)
    return "c++" in syntax.casefold()
