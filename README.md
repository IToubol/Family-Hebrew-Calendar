# Family-Hebrew-Calendar

Generates a printable A2 PDF calendar displaying Hebrew and Gregorian dates
side by side, with family birthdays and Jewish holidays highlighted.

## Features

- Full year calendar in Hebrew month layout
- Each cell shows the Hebrew date + corresponding Gregorian date and weekday
- Jewish holidays color-coded (Yom Tov, Hol Hamoed, special days)
- Family birthdays displayed inside the relevant date cells
- Shabbat highlighted
- Background image support (place a `.jpg`/`.png` in the folder)

## Output

A single A2 landscape PDF file: `calendrier-{year}.pdf`

## Stack

- Python 3
- ReportLab
- unidecode
- `calendarcomputing.py` (Hebrew calendar logic — see hebrew-date-converter repo)

## Setup

```bash
pip install reportlab unidecode
```

## Architecture
```
./Family-Hebrew-Calendar
   └── anniversaires.txt
   └── calendrier-5784.pdf
   └── create-calendar.bat
   └── factory
         └── calendarcomputing.py
         └── constants.py
         └── hd_roses.jpeg
         └── pdfgeneration.py
         └── practical_example.url
         └── ressources.txt
         └── user.py
```

Add a file `anniversaires.txt` at the parent level with this format *(day, Hebrew month, name)*:
```
15,Nissan,Salomon
3,Tichri,Sarah
```
#### Months syntaxe
`Tichri, Hechvan, Kislev, Tevet, Chevat, Adar-A, Adar-b, Nissan, Iyar, Sivan, Tamouz, Av, Eloul`

Then (on windows) double-click on `create-calendar.bt` or run:
```bash
python3 pdfgeneration.py
```

## Notes

- Depends on `calendarcomputing.py` for Hebrew date computations
- Handles leap years (Adar Aleph/Bet) and variable month lengths automatically
