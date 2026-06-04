CYCLE_CUMULS: tuple[tuple[int]] = (
    (0, 0, 0), (4, 8, 876), (1, 17, 672), (0, 15, 181),
    (4, 23, 1057), (2, 8, 853), (1, 6, 362), (5, 15, 158),
    (4, 12, 747), (1, 21, 543), (6, 6, 339), (5, 3, 928),
    (2, 12, 724), (6, 21, 520), (5, 19, 29), (3, 3, 905),
    (0, 12, 701), (6, 10, 210), (3, 19, 6),
)

# Molad Tohou marks the initial molad of year 1.
# It precedes the day of the creation of the first man by one year.
# This molad occurred on a Monday, corresponding to the second day of the week.
# As a result, only a single complete day is factored into the calculation of this molad's value.
MOLAD_TOHOU: tuple[int] = 1, 5, 204

CYCLE_YTARON: tuple[int] = 2, 16, 595

YTARON_PECHOUTA: tuple[int] = 4, 8, 876

YTARON_MEOUBERET: tuple[int] = 5, 21, 589

HOUR_PARTS: int = 1080

HEBREW_MONTHS: list[str] = [
   "תשרי", "חשוון", "כסלו", "טבת",
    "שבט", "אדר", "ניסן", "אייר",
    "סיון", "תמוז", "אב", "אלול",
]

BASE_FRENCH_HEBREW_MONTHS: list[str] = [
    "Tichri", "Hechvan", "Kislev", "Tevet",
    "Chevat", "Adar", "Nissan", "Iyar",
    "Sivan", "Tamouz", "Av", "Eloul"
]

FRENCH_CIVILS_MONTHS: tuple[str] = (
    "Janvier", "Fevrier", "Mars", "Avril",
    "Mai", "Juin", "Juillet", "Aout",
    "Septembre", "Octobre", "Novembre", "Decembre",
)

HEBREW_CIVILS_MONTHS: tuple[str] = (
    "ינואר", "פברואר", "מרץ", "אפריל",
    "מאי", "יוני", "יולי", "אוגוסט",
    "ספטמבר", "אוקטובר", "נובמבר", "דצמבר",
)

HEB_CIVILS_MONTHS_TO_NUMBERS: dict[str:int] = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12,
}

CONVERT_DAYS: dict[str:str] = {
    "1": "א", "2": "ב", "3": "ג", "4": "ד", "5": "ה", "6": "ו",
    "7": "ז", "8": "ח", "9": "ט", "10": "י", "11": "יא", "12": "יב",
    "13": "יג", "14": "יד", "15": "טו", "16": "טז", "17": "יז", "18": "יח",
    "19": "יט", "20": "כ", "21": "כא", "22": "כב", "23": "כג", "24": "כד",
    "25": "כה", "26": "כו", "27": "כז", "28": "כח", "29": "כט", "30": "ל",
}

FRENCH_WEEK_DAYS: tuple[str] = ("Samedi", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi")

HEBREW_WEEK_DAYS: tuple[str] = ("שבת", "ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי")

CIVIL_TO_HEBREW_OFFSET = 1373073  # 1 Janvier 0001  ==  שני 18 טבת 3761
