from collections import defaultdict
from datetime import datetime, timedelta
from locale import LC_TIME, setlocale
from os import listdir
from os.path import splitext
from unidecode import unidecode # Pour enlever les accents des noms des mois

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A2 as PAGE_SIZE

from calendarcomputing import Chana, convertHC
from user import year_choice


setlocale(LC_TIME, "FR")

PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE # inverser (ici et dans la suite) l'ordre de la hauteur et largeur
                                    # pour une orientation paysage (ce que fait la fonction landscape de .pagesizes)
PADDING_SIDE = 15
PADDING_BOTTOMUP = 7

USER_YEAR_CHOICE = year_choice()
YEAR = int(USER_YEAR_CHOICE)
TITLE = f"CALENDAR {YEAR}"
ROSH_HASHANA = (1, 1, YEAR)

CHANA = Chana(YEAR)
MONTHS_NB = 12 + CHANA.isbissextile

KISLEV_MISS = CHANA.offset == 0

MONTHS = CHANA.months()

YOM_TOV_COLOR = colors.HexColor(0x8DB9B5)
HOL_HAMOED_COLOR = colors.HexColor(0x96E4CF)
SPECIAL_DAYS_COLOR = colors.lightgreen

ROW_HEIGHT = (PAGE_HEIGHT - PADDING_BOTTOMUP * 2) / 32
CELL_WIDTH = (PAGE_WIDTH - PADDING_SIDE * 2) / MONTHS_NB

INITIAL_Y = PAGE_HEIGHT - PADDING_BOTTOMUP - ROW_HEIGHT
COLUMN_HEAD = INITIAL_Y - ROW_HEIGHT

HOLLIDAYS_DATA: dict[tuple:tuple] = {
    **{("Tichri", yom): ("Roch Hachana", YOM_TOV_COLOR) for yom in (1, 2)},
    ("Tichri", 10): ("Yom Kipour", YOM_TOV_COLOR),
    **{("Tichri", yom): ("Soucot", YOM_TOV_COLOR) for yom in (15, 16, 22, 23)},
    **{("Tichri", yom): ("Soucot", HOL_HAMOED_COLOR) for yom in range(17, 22)},
    **{("Kislev", yom): ("Hanouka", SPECIAL_DAYS_COLOR) for yom in range(25, 30)},
    (("Kislev", "Tevet")[KISLEV_MISS], (30, 1)[KISLEV_MISS]): ("Hanouka", SPECIAL_DAYS_COLOR),
    ("Tevet", (1, 2)[KISLEV_MISS]): ("Hanouka", SPECIAL_DAYS_COLOR),
    ("Tevet", (2, 3)[KISLEV_MISS]): ("Hanouka", SPECIAL_DAYS_COLOR),
    ("Chevat", 15): ("Tou Bichvat", SPECIAL_DAYS_COLOR),
    ("Adar-B" if CHANA.isbissextile else "Adar", 14): ("Pourim", SPECIAL_DAYS_COLOR),
    **{("Nissan", yom): ("Pessah", YOM_TOV_COLOR) for yom in (15, 16, 21, 22)},
    **{("Nissan", yom): ("Pessah", HOL_HAMOED_COLOR) for yom in range(17, 21)},
    ("Sivan", 6): ("Chavouot", YOM_TOV_COLOR), ("Sivan", 7): ("Chavouot", YOM_TOV_COLOR),
}


BIRTHDAY_DATA = defaultdict(list)
with open(r"..\anniversaires.txt", encoding="utf-8") as file:
    for line in file:
        yom, hodesh, name = line.strip().split(",")
        yom = int(yom)

        if hodesh not in MONTHS:
            hodesh = "Adar"

        if yom > MONTHS[hodesh]:
            yom = 1
            if hodesh == "Hechvan":
                hodesh = "Kislev"
            elif hodesh == "Kislev":
                hodesh = "Tevet"
            elif hodesh == "Adar":
                hodesh = "Nissan"

        BIRTHDAY_DATA[(yom, hodesh)].append(name.encode("utf-8"))


def draw_cell(color:colors) -> None:
    pdf.setFillColor(color)
    pdf.rect(x, y, CELL_WIDTH, ROW_HEIGHT, 1, 1)

def write_text(x:float, y:float, text:str, font:str = None, size:int = None, color:colors = None) -> None:
    if font is not None and size is not None:
        pdf.setFont(font, size)
    if color is not None:
        pdf.setFillColor(color)
    pdf.drawCentredString(x, y, text=text)


pdf = Canvas(f"../calendrier-{YEAR}.pdf", pagesize=PAGE_SIZE)
pdf.setTitle(TITLE)
for name in listdir():
    if splitext(name)[1] in {".jpeg", ".png", ".jpg"}:
        pdf.drawImage(name, 0, 0, width=PAGE_SIZE[0], height=PAGE_SIZE[1])
        break
pdf.setStrokeColor(colors.olive)

write_text(PAGE_WIDTH / 2, INITIAL_Y + 10, USER_YEAR_CHOICE, "Times-Bold", ROW_HEIGHT - 6)

x,y = PADDING_SIDE, COLUMN_HEAD
civil_date = datetime(*convertHC(ROSH_HASHANA)[:3])

for hodesh in MONTHS:
    draw_cell(colors.HexColor(0xFFFF88))
    write_text(x + CELL_WIDTH / 2, y + ROW_HEIGHT / 2 - 5, hodesh, "Times-Bold", 15, colors.maroon)
    
    for yom in range(1, MONTHS[hodesh] + 1):
        y -= ROW_HEIGHT

        weekday, day, month, year = civil_date.strftime("%a %d %b %Y").split()
        weekday = weekday.strip(".").upper()

        cell_color = HOLLIDAYS_DATA[(hodesh, yom)][1] if (hodesh, yom) in HOLLIDAYS_DATA else colors.lightpink if weekday == "SAM" else colors.lightcyan    
        draw_cell(cell_color)

        heb_date = f"{yom}  {HOLLIDAYS_DATA[(hodesh, yom)][0]}" if (hodesh, yom) in HOLLIDAYS_DATA else str(yom)
        write_text(x + CELL_WIDTH / 2, y + ROW_HEIGHT - 12, heb_date, "Times-Bold", 12, colors.black)

        civ_date = f"{"CHABAT" if weekday == "SAM" else weekday} {day.capitalize()} {unidecode(month.rstrip(".")).upper()} {year}"
        write_text(x + CELL_WIDTH / 2, y + 2, civ_date, "Times-Roman", 8)

        if (yom, hodesh) in BIRTHDAY_DATA:
            names_nb = len(BIRTHDAY_DATA[(yom, hodesh)])
            interline = (ROW_HEIGHT - 26) // names_nb
            for i in range(names_nb):
                write_text(x     = x + CELL_WIDTH / 2,
                           y     = y + ROW_HEIGHT - (17 + interline * (i + .6)),
                           text  = BIRTHDAY_DATA[(yom, hodesh)][i].decode("utf-8"),
                           font  = "Times-Bold",
                           size  = 12,
                           color = colors.darkred)

        civil_date += timedelta(days=1)
    
    if yom == 29:
        y -= ROW_HEIGHT
        draw_cell(colors.transparent)
    
    x += CELL_WIDTH
    y = COLUMN_HEAD

pdf.save()
