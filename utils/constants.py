# Not sure if this is the correct or best way to do any of this

# Text formatting constants
TAB: str = "     "

def TABS(self, number: int) -> str:
    """Return a specified number of TABs."""
    return self.TAB * number

# Constants for working with US state names and abbreviations
STATES: dict[int, int] = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware'
    , 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas'
    , 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota'
    , 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey'
    , 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon'
    , 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah'
    , 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}
STATE_ABBRS: list[str] = sorted(list(STATES.keys()))
STATE_NAMES: list[str] = sorted(list(STATES.values()))

def STATE_ABBR(name: str) -> str:
    """
    Return state name given abbreviation if it exists, otherwise return
    abbreviation.
    """
    if name in STATES.values():
        return list(STATES.keys())[list(STATES.values()).index(name)]
    else:
        return name

def STATE_NAME(abbr: str) -> str:
    """Return state abbreviation given name if it exists, otherwise return name."""
    if abbr in STATES.keys():
        return STATES[abbr]
    else:
        return abbr