from __future__ import annotations
from sys import argv


from constants import (
    CYCLE_YTARON,
    CYCLE_CUMULS,
    MOLAD_TOHOU,
    HOUR_PARTS,
    FRENCH_WEEK_DAYS,
    CIVIL_TO_HEBREW_OFFSET,
    BASE_FRENCH_HEBREW_MONTHS
)


class Ytaron:
    def __init__(self, days: int = 1, hours: int = 12, parts: int = 793) -> None:
        self.days = days
        self.hours = hours
        self.parts = parts

    def __repr__(self) -> str:
        return f"Ytaron{(self.days, self.hours, self.parts)}"

    def __add__(self, other: tuple | Ytaron) -> Ytaron:
        if isinstance(other, tuple):
            parts = self.parts + other[2]
            hours = self.hours + other[1] + parts // HOUR_PARTS
            days = self.days + other[0] + hours // 24

        elif isinstance(other, Ytaron):
            parts = other.parts + self.parts
            hours = other.hours + self.hours + parts // HOUR_PARTS
            days = other.days + self.days + hours // 24

        return Ytaron(days % 7, hours % 24, parts % HOUR_PARTS)

    def __mul__(self, number: int) -> Ytaron:
        parts = self.parts * number
        hours = self.hours * number + parts // HOUR_PARTS
        days = self.days * number + hours // 24
        return Ytaron(days % 7, hours % 24, parts % HOUR_PARTS)


def molad_of(year:int) -> Ytaron:
    cycles_nb, rank = divmod(year, 19)
    rank = rank or 19
    cycles_nb -= (rank == 19)
    return Ytaron(*CYCLE_YTARON) * cycles_nb + MOLAD_TOHOU + CYCLE_CUMULS[rank - 1]


def rosh_hashana_day(molad:Ytaron, rank:int) -> int:
    day = molad.days + (
        # מולד זקן בל תדרוש
        molad.hours > 17
        # ג"ט ר"ד בשנה פשוטה גרוש
        or (
            rank in {1, 2, 4, 5, 7, 9, 10, 12, 13, 15, 16, 18}
            and molad.days == 2
            and (molad.hours > 9 or (molad.hours == 9 and molad.parts > 203))
        )
        # ב' ט"ו תקפ"ט לאחר העיבור עקור מלשרוש
        or (
            rank in {1, 4, 7, 9, 12, 15, 18}
            and molad.days == 1
            and (molad.hours > 15 or (molad.hours == 15 and molad.parts > 588))
        )
    )
    day += day in {0, 3, 5, 7}  # לא אד"ו ראש
    return day + 1


class Chana:
    def __init__(self, year: int) -> None:
        self.year: int = year # for the repr method

        # very util variable for bellow computings:
        rank = year % 19 or 19

        # bissextile determination:
        self.isbissextile: int = rank in {3, 6, 8, 11, 14, 17, 19}

        # offset computing:
        current_year_molad = molad_of(year)
        self.roshAshana = 6 if year == 2 else rosh_hashana_day(current_year_molad, rank)
        next_year_molad = molad_of(year + 1)
        next_roshAshana = (6 if year == 1 else rosh_hashana_day(next_year_molad, (rank + 1) % 19 or 19))
        self.offset = (year if year < 3 else (next_roshAshana - self.roshAshana - 3 - self.isbissextile * 2) % 7)

    # year months computing:
    def months(self) -> dict[str, int]:
        months_lenghts = (  # from Tichri to Eloul
            30, 29 + (self.offset == 2), 29 + (self.offset > 0),
            29, 30, 29 + self.isbissextile, 30 - self.isbissextile,
            29 + self.isbissextile, 30 - self.isbissextile,
            29 + self.isbissextile, 30 - self.isbissextile,
            29 + self.isbissextile, 29)[:12 + self.isbissextile]

        month_names = BASE_FRENCH_HEBREW_MONTHS[:] # important de faire une copie:
                                            # cette liste peut être utilisée des milliers de fois (convertHC),
                                            # et doit pouvoir se réinitialiser à chaque fois (effet de bord Python).
        if self.isbissextile:
            month_names[5] += "-A"
            month_names.insert(6, "Adar-B")

        return {month:len for month,len in zip(month_names, months_lenghts)}

    def __repr__(self):
        return f"""Chana({self.year})
{('pechouta', 'meouberet')[self.isbissextile]}
rank: {self.year % 19 or 19}
Roch hachana: {self.roshAshana}
offset: {self.offset}"""


class Taarikh:
    def __init__(self, day: int, month: int, year: int) -> None:
        self.chana = Chana(year)

        # date validity test
        if (
            ((year < 1) or (day < 1) or (day > 30))
            or (month > 12 + self.chana.isbissextile)
            or (month == 4 and day > 29)
            or (month - self.chana.isbissextile in {6, 8, 10, 12} and day > 29)
            or (month == 2 and self.chana.offset < 2 and day > 29)
            or (month == 3 and self.chana.offset == 0 and day > 29)
        ):
            raise ValueError(f"\nInvalide date: {day}/{month}/{year}")

        self.day = day
        self.month = month
        self.year = year
        zero_days = self.chana.roshAshana - 1

        # weekday computing
        months_lenghts = list(self.chana.months().values())
        self.weekday = FRENCH_WEEK_DAYS[(zero_days + sum(months_lenghts[: month - 1]) + day) % 7]

    def __add__(self, number: int) -> Taarikh:
        return yamim_to_taarikh(taarikh_to_yamim(self) + number)

    def __sub__(self, other: int|tuple) -> int | Taarikh:
        if isinstance(other, int):
            return yamim_to_taarikh(taarikh_to_yamim(self) - other)
        if isinstance(other, tuple) or isinstance(other, Taarikh):
            return taarikh_to_yamim(self) - taarikh_to_yamim(other)

    def __repr__(self) -> str:
        return f"{self.weekday} {self.day} {tuple(self.chana.months().keys())[self.month-1]} {self.year}"

    def __eq__(self, other: tuple|Taarikh) -> bool:
        if isinstance(other, tuple):
            day, month, year = other
        elif isinstance(other, Taarikh):
            day, month, year = other.day, other.month, other.year

        return self.day == day and self.month == month and self.year == year

    def __lt__(self, other: tuple|Taarikh) -> bool:
        if isinstance(other, tuple):
            day, month, year = other
        elif isinstance(other, Taarikh):
            day, month, year = other.day, other.month, other.year

        if self.year != year:
            return self.year < year
        if self.month != month:
            return self.month < month
        return self.day < day

    def __gt__(self, other: object) -> bool:
        return other < self


def taarikh_to_yamim(taarikh: Taarikh|tuple[int]) -> int:
    if isinstance(taarikh, Taarikh):
        days, month, year, offset, B = (
            taarikh.day, taarikh.month, taarikh.year, taarikh.chana.offset, taarikh.chana.isbissextile
        )

    elif isinstance(taarikh, tuple):
        days, month, year = taarikh
        chana = Chana(year)
        offset, B = chana.offset, chana.isbissextile

    if year < 2:
        raise ValueError("Days computation starts from head of the year 2")

    days += sum((
        30, 29 + (offset == 2), 29 + (offset > 0), 29, 30, 29 + B,
        30 - B, 29 + B, 30 - B, 29 + B, 30 - B, 29 + B)[: month - 1])

    while year > 3:  # not year 2 in loop while her offset is exceptional (rosh hashana in friday)
        year -= 1
        chana = Chana(year)
        days += 353 + chana.offset + (30 if chana.isbissextile else 0)
    days += 355  # to add 355 days of the year 2

    return days


def yamim_to_taarikh(days: int) -> Taarikh:
    if days > 0:
        year = 2
        year_lenght = 355
        chana = Chana(year)

        while days >= year_lenght:
            days -= year_lenght
            year += 1
            chana = Chana(year)
            year_lenght = 353 + chana.offset + (30 if chana.isbissextile else 0)
        else:
            if not days:
                year -= 1
                isbissextile = year % 19 in {0, 3, 6, 8, 11, 14, 17}
                return Taarikh(29, 12 + isbissextile, year)

        B = chana.isbissextile

        months_lenghts = (
            30, 29 + (chana.offset == 2),
            29 + (chana.offset > 0), 29, 30,
            29 + B, 30 - B, 29 + B, 30 - B,
            29 + B, 30 - B, 29 + B, 29,
        )
        month = 0
        while days > months_lenghts[month]:
            days -= months_lenghts[month]
            month += 1

        return Taarikh(days, month + 1, year)


def days_to_date(days: int) -> tuple[int]:
    "Converts a number of days in a civil date."

    weekday = FRENCH_WEEK_DAYS[(days + 1) % 7]
    # weekday = HEBREW_WEEK_DAYS[(days+1) % 7]

    centuries4_number = days // 146097
    days %= 146097

    centuries_number = days // 36524
    days %= 36524
    if centuries_number == 4:
        centuries_number = 3
        days += 36524

    years4 = days // 1461
    days %= 1461

    years = days // 365
    days %= 365
    if years == 4:
        years = 3
        days += 365

    if not days:
        return (weekday, 31, 12, centuries4_number * 400 + centuries_number * 100 + years4 * 4 + years,)

    years += 1

    cumuls = (
        31, 28 + (0 if years % 4 or (years4 == 24 and centuries_number % 4) else 1),
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    )

    month = 0
    while days > cumuls[month]:
        days -= cumuls[month]
        month += 1

    return centuries4_number * 400 + centuries_number * 100 + years4 * 4 + years, month + 1, days, weekday # isoformat = YYYY-mm-dd (and weekday 0 == sunday)


def date_to_days(date: tuple) -> int:
    """
    Converts a civil date in a number of days
    (from the monday 01/01/0001 of the Georgian civil calendar).
    """
    days, month, year = date
    years = year - 1

    days += (years // 400) * 146097
    years %= 400

    days += (years // 100) * 36524
    years %= 100

    days += (years // 4) * 1461
    years %= 4

    days += years * 365

    B = 0 if (year % 4 or (year % 100 == 0 and year % 400)) else 1
    cumuls = ( 0, 31, 59 + B, 90 + B, 120 + B, 151 + B, 181 + B, 212 + B, 243 + B, 273 + B, 304 + B, 334 + B)

    return days + cumuls[month - 1]


def convertHC(date: Taarikh|tuple[int]) -> tuple[int]:
    return days_to_date(taarikh_to_yamim(date) - CIVIL_TO_HEBREW_OFFSET)


def convertCH(date: tuple) -> Taarikh:
    return yamim_to_taarikh(date_to_days(date) + CIVIL_TO_HEBREW_OFFSET)



# print(date_to_days((13,7,1981)))
# print("\ntaarikh-yamim: ", taarikh_to_yamim((11,11,5741))) # 2096447
# print("yamim-taarikh: ", yamim_to_taarikh(2096447))


# annivs = {
#     "Israel:  ":{'civil': (13,7,1981), 'heb': (11,11,5741)},
#     "Hilanie: ":{'civil':(27,9,1983), 'heb': (21,1,5744)},
#     "Baroukh: ":{'civil':(9,2,2004), 'heb': (17,5,5764)},
#     "Tova:    ":{'civil':(3,1,2005), 'heb': (22,4,5765)},
#     "Eliahou: ":{'civil':(14,1,2006), 'heb': (14,4,5766)},
#     "Moché:   ":{'civil':(13,3,2011), 'heb': (7,7,5771)},
#     "Hava     ":{'civil':(31,8,2012), 'heb': (13,12,5772)}
# }
# print("\n\t\tTests")
# for name in annivs:
#     print("\n",name)
#     print("\t\tTests de conversions\n\t\tjours-date / date-jours (hebr)")
#     yamim = taarikh_to_yamim(annivs[name]['heb'])
#     taarikh = yamim_to_taarikh(yamim)
#     print("\n\tOriginale = ", annivs[name]['heb'])
#     print("\tTransformée = ", taarikh)

#     print("\n\t\tTests de conversions\n\t\tciviles -> hebraiques\n\t\thebraiques <- civiles")
#     HC = convertHC(annivs[name]['heb'])
#     CH = convertCH(annivs[name]['civil'])
#     print("\n\tCivile:      ", *annivs[name]['civil'], "    -> Hebraique:", CH)
#     print( "\tCivile:", HC, "<- Hebraique:    ", *annivs[name]['heb'],)
#     print("\n-----------------------------------------------------------------------")

# joursDepuis0 = date_to_days((7,1,2024))
# yamimMiefess = taarikh_to_yamim((26,4,5784))
# print(yamim_to_taarikh(yamimMiefess - joursDepuis0))


if __name__ == "__main__":
    if len(argv) > 1:
        choix, date = argv[1], argv[2]
        jour, mois, annee = map(int, date.split("/"))
        print(
            convertCH((jour, mois, annee))
            if choix == "ch"
            else convertHC((jour, mois, annee))
        )

    # else:
    #     choix = input("Conversion H -> C [hc] ou C -> H ? [ch] ")
    #     if choix == "hc":
    #         date = input("date: [annee mois jour]").split()
    #         if len(date) == 3:
    #             try:
    #                 annee, mois, jour = map(int, date)
    #             except Exception as e:
    #                 print(e)
    #                 exit()
