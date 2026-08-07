"""Per-category meat cut synonym maps for fuzzy product matching.

Each key is a canonical cut; each value is a list of aliases that
resolve to that canonical cut. Maps are matched against normalized
product names (lowercase, punctuation removed) — see matcher.py.
"""

# Canonical cut -> aliases (lowercase, no punctuation)
CUT_SYNONYMS = {
    "beef": {
        "ground beef": [
            "hamburger", "ground chuck", "ground round", "ground sirloin",
            "ground beef", "beef patties", "beef patty", "lean ground beef",
        ],
        "chuck roast": ["chuck roast", "chuck steak", "pot roast", "chuck"],
        "flank steak": ["flank steak", "flank"],
        "skirt steak": ["skirt steak", "skirt"],
        "sirloin steak": ["sirloin steak", "sirloin", "beef loin"],
        "sirloin tip": ["sirloin tip", "sirloin tip roast"],
        "ribeye": ["ribeye", "rib eye", "rib eye steak", "ribeye steak", "eye of rib"],
        "ny strip": ["ny strip", "new york strip", "strip steak", "top loin steak"],
        "tri-tip": ["tri tip", "tri tip roast", "tri-tip"],
        "brisket": ["brisket", "brisket flat", "brisket point"],
        "short ribs": ["short ribs", "beef ribs", "back ribs", "short rib"],
        "oxtail": ["oxtail", "ox tail"],
        "stew meat": ["stew meat", "beef stew meat", "stew beef", "stewing beef"],
        "beef liver": ["beef liver", "liver"],
        "corned beef": ["corned beef", "corn beef"],
        "roast": ["beef roast", "arm roast", "bottom round roast", "rump roast", "eye round roast"],
    },
    "pork": {
        "pork chops": ["pork chops", "pork chop", "loin chops", "bone-in chops", "pork loin chop"],
        "bacon": ["bacon", "thick cut bacon", "applewood bacon", "smoked bacon"],
        "pork sausage": ["pork sausage", "ground pork", "sausage links", "breakfast sausage"],
        "pork shoulder": ["pork shoulder", "pork butt", "boston butt", "pork picnic"],
        "pork belly": ["pork belly", "belly"],
        "pork ribs": ["pork ribs", "spareribs", "baby back ribs", "country ribs", "spare ribs"],
        "pork loin": ["pork loin", "loin roast", "pork roast"],
        "pork tenderloin": ["pork tenderloin", "tenderloin"],
        "ham": ["ham", "ham steak", "smoked ham", "country ham"],
        "pork leg": ["pork leg", "fresh ham", "pork shank"],
    },
    "chicken": {
        "breast": ["breast", "breasts", "chicken breast", "chicken breasts", "boneless breast",
                   "boneless breasts", "b s breast", "b/s breast", "bs breast", "skinless breast"],
        "thigh": ["thigh", "thighs", "chicken thigh", "chicken thighs", "boneless thigh"],
        "drumstick": ["drumstick", "drumsticks", "legs", "leg quarters"],
        "wings": ["wings", "wing", "chicken wings", "wingettes"],
        "whole": ["whole chicken", "whole fryer", "roaster", "fryer", "roaster chicken"],
        "ground": ["ground chicken", "chicken sausage"],
        "tenderloin": ["tenderloins", "chicken tender", "chicken tenders", "tenders"],
    },
    "turkey": {
        "whole": ["whole turkey", "turkey"],
        "ground": ["ground turkey", "turkey sausage", "turkey burger"],
        "breast": ["turkey breast", "turkey breasts", "boneless turkey breast"],
        "thigh": ["turkey thigh", "turkey thighs"],
        "wing": ["turkey wing", "turkey wings"],
        "drumstick": ["turkey drumstick", "turkey legs"],
    },
    "seafood": {
        "salmon": ["salmon", "salmon fillets", "salmon fillet", "atlantic salmon",
                   "wild salmon", "salmon steaks", "fresh salmon"],
        "shrimp": ["shrimp", "raw shrimp", "cooked shrimp", "jumbo shrimp",
                   "medium shrimp", "tail-on shrimp", "peeled shrimp"],
        "cod": ["cod", "cod fillets", "atlantic cod", "pacific cod"],
        "tilapia": ["tilapia", "tilapia fillets"],
        "trout": ["trout", "rainbow trout"],
        "halibut": ["halibut", "halibut fillets"],
        "crab": ["crab", "crab legs", "king crab", "dungeness crab", "crab meat"],
        "lobster": ["lobster", "lobster tails", "lobster tail"],
        "scallops": ["scallops", "sea scallops", "bay scallops"],
        "clams": ["clams", "steamer clams", "littleneck clams"],
        "mussels": ["mussels"],
        "oysters": ["oysters"],
        "tuna": ["tuna", "tuna steaks", "ahi tuna", "yellowfin"],
        "catfish": ["catfish", "catfish fillets"],
        "swai": ["swai", "basa"],
        "imitation crab": ["imitation crab", "surimi"],
    },
}

# Canonical category names used as keys in CUT_SYNONYMS
CATEGORY_KEYS = ["beef", "pork", "chicken", "turkey", "seafood"]
