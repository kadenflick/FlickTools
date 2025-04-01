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

    return list(STATES.keys())[list(STATES.values()).index(name)] if name in STATES.values() else name

def STATE_NAME(abbr: str) -> str:
    """Return state abbreviation given name if it exists, otherwise return name."""

    return STATES[abbr] if abbr in STATES.keys() else abbr
    
# Constants for compliments
COMPLIMENTS: list[str] = [
    "Today you were a hero.", "How's the view from the top of the world?", "Your grandma must be very proud of you."
    , "You're fiercely self-motivated.", "You are awesome!", "You have impeccable hair.", "You deserve a hug right now."
    , "You should be proud of yourself.", "You're more helpful than you realize.", "You've got an awesome sense of humor!", "You're so brave."
    , "On a scale from 1 to 10, you're an 11.", "Crank it to 11!", "You're even more beautiful on the inside than you are on the outside."
    , "You have the courage of your convictions.", "You're like a ray of sunshine on a really dreary day.", "You are making a difference."
    , "You bring out the best in other people.", "Everything would be better if more people were like you!", "I bet you sweat glitter."
    , "Everything you touch turns to gold.", "You were cool way before hipsters were cool.", "You help others feel more joy in life."
    , "You may dance like no one's watching, but everyone's watching because you're an amazing dancer!"
    , "You're more fun than a ball pit filled with candy.", "That thing you don't like about yourself is what makes you so interesting."
    , "You're wonderful.", "You're better than a triple-scoop ice cream cone with sprinkles."
    , "If you were a box of crayons, you'd be the giant name-brand one with the built-in sharpener."
    , "You should be thanked more often. So thank you!!", "Our community is better because you're in it.", "You have the best ideas."
    , "You always find something special in the most ordinary things.", "You're a candle in the darkness.", "You're a great example to others."
    , "Being around you is like being on a happy little vacation."
    , "You're always learning new things and trying to better yourself, which is commendable."
    , "If someone based an Internet meme on you, it would have impeccable grammar.", "You're more fun than bubble wrap."
    , "You're like a breath of fresh air.", "Your creative potential is limitless."
    , "When you make up your mind about something, nothing stands in your way.", "Any team would be lucky to have you on it."
    , "I'll bet you do the crossword puzzle in ink.", "Babies and small animals probably love you.", "You're someone's reason to smile."
    , "You're even better than a unicorn.", "You have a good head on your shoulders.", "Has anyone ever told you that you have great posture?"
    , "Thank you for being you.", "Even if you were cloned, you'd still be one of a kind.", "You're smarter than Google and Mary Poppins combined."
    , "You're not someone I pretend to not see in public.", "You are like a corner piece of a puzzle.", "Are you a beaver, because damn."
    , "I bet you make babies smile.", "You are more wonderful than the smell of a new book.", "You could survive a zombie apocalypse."
]