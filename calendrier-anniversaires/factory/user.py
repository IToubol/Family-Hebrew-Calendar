from os import name, system
from sys import exit
from time import sleep


def clear_screen() -> None:
    system("cls" if name == "nt" else "clear")

def year_choice() -> str:
    clear_screen()

    user_year_choice = input("""\n
        Saisir l'année hébraïque pour laquelle
        vous souhaitez éditer le calendrier
        (un nombre entier plus grand que 3760)
        (Pour quitter le processus, taper q):
        
        >>>  """)
    
    if not (user_year_choice.isdigit() and int(user_year_choice) > 3760):
        clear_screen()
    
        if user_year_choice in {"q", "Q"}:
            print("""\n\n\n
        AUREVOIR . . .""")
            sleep(2)
            exit()
    
        print("""\n\n\n
        Saisie invalide . . .""")
        sleep(1)
        return year_choice()
    
    return user_year_choice

if __name__ == "__main__":
    print(year_choice())