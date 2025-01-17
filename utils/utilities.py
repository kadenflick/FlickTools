# Not sure if this is the correct or best way to do any of this
# Probably pretty bad
class Formatting():
    TAB: str = "     "

    def __init__(self):
        pass

    def TABS(self, number: int) -> str:
        """ Return a specified number of TABs. """
        return self.TAB * number

class States():
    _STATES: dict[int, int] = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE'
        ,'Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY'
        ,'Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO'
        ,'Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC'
        ,'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC'
        ,'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV'
        ,'Wisconsin':'WI','Wyoming':'WY'
    }
    
    STATE_NAMES: list[str] = sorted(list(_STATES.keys()))
    STATE_ABBRS: list[str] = sorted(list(_STATES.values()))

    def __init__(self):
        pass
    
    def STATE_NAME(self, abbr: str) -> str:
        """ Return state name given abbreviation if it exists, otherwise return abbreviation. """
        if abbr in self._STATES.values():
            return list(self._STATES.keys())[list(self._STATES.values()).index(abbr)]
        else:
            return abbr
    
    def STATE_ABBR(self, name: str) -> str:
        """ Return state abbreviation given name if it exists, otherwise return name. """
        if name in self._STATES.keys():
            return self._STATES[name]
        else:
            return name