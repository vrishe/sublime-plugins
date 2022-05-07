class AnonymousObject:
  def __init__(self, d: dict):
    def recursive_check(obj):
      for key, value in d.items():
        if isinstance(value, dict):
          value = Anon(value)
        setattr(obj, key, value)
    recursive_check(self)