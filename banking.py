import random
import sqlite3


CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER PRIMARY KEY,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0    
    )
    '''

INSERT_CARD = '''
        INSERT INTO card (number, pin, balance)
        VALUES (?, ?, ?)
    '''

DB_LOGIN = '''
        SELECT *
        FROM card
        WHERE number = ? AND pin = ?; 
    '''

DB_BALANCE = '''
        SELECT balance
        FROM card
        WHERE number = ?; 
    '''

DB_ADD_INCOME = '''
        UPDATE card
        SET balance = balance + ?
        WHERE number = ?;
    '''


DB_DELETE_ACCOUNT = '''
        DELETE
        FROM card
        WHERE number = ? AND pin = ?;
    '''

DB_CHECK_NUMBER = '''
    SELECT *
    FROM card
    WHERE number = ?
    '''


def add_card(connection, number, pin, balance):
    with connection:
        cur.execute(INSERT_CARD, (number, pin, balance))


def login(connection, card, pin):
    with connection:
        return connection.execute(DB_LOGIN, (card, pin)).fetchone()


def check_balance(connection, card):
    with connection:
        return connection.execute(DB_BALANCE, (card,)).fetchone()


def add_income(connection, card):
    with connection:
        income = cur.execute(DB_ADD_INCOME, (int(input("Enter income:")), card))
    print("Income was added!")
    return income


def check_luhn(number):
    control_number = 0
    index = 1
    for num in str(number):
        tmp = int(num)
        if index % 2 != 0:
            tmp *= 2
            if tmp > 9:
                tmp -= 9
        if index <= 15:
            control_number += tmp
        index += 1
    if (control_number + int(str(number)[15])) % 10 == 0:
        return 1
    else:
        return 0


def do_transfer(connection, card, pin):
    print("Transfer")
    transfer_card_number = int(input("Enter card number:"))
    if transfer_card_number == card:
        print("You can't transfer money to the same account!")
    else:
        if check_luhn(transfer_card_number):
            if cur.execute(DB_CHECK_NUMBER, (transfer_card_number,)).fetchone():
                amount = int(input("Enter how much money you want to transfer:"))
                card_balance = check_balance(connection, card)[0]
                if amount <= card_balance:
                    with connection:
                        cur.execute(DB_ADD_INCOME, (amount, transfer_card_number))
                    with connection:
                        cur.execute(DB_ADD_INCOME, (-amount, card))
                else:
                    print("Not enough money!")
            else:
                print("Such a card does not exist.")
        else:
            print("Probably you made a mistake in the card number. Please try again!")


def close_account(connection, card, pin):
    with connection:
        connection.execute(DB_DELETE_ACCOUNT, (card, pin))
    print("The account has been closed!")


class CreditCard:
    number = None
    pin = None
    balance = None
    all_cards = []

    def __init__(self):
        control_number = 0
        self.number = "400000{}".format(random.randint(100000000, 999999999))

        index = 1
        for num in str(self.number):
            tmp = int(num)

            if index % 2 != 0:
                tmp *= 2
                if tmp > 9:
                    tmp -= 9
            index += 1
            control_number += tmp

        if control_number % 10 != 0:
            checksum = 10 - (control_number % 10)
        else:
            checksum = 0

        self.number = str(self.number) + str(checksum)
        self.pin = str(random.randint(0000, 9999)).zfill(4)
        self.balance = 0
        CreditCard.all_cards.append(self)

        with connection:
            add_card(connection, self.number, self.pin, 0)

        print("Your card has been created")
        print("Your card number:\n{}".format(self.number))
        print("Your card PIN:\n{}".format(self.pin))
        print("")

def menu():
    exit = False

    while exit == False:
        print("""
        1. Create an account
        2. Log into account
        0. Exit
        """"")
        menu_selection = int(input())

        if menu_selection == 1:
            new_card = CreditCard()
            print("")
            continue
        elif menu_selection == 2:
            card_number = input("Enter your card number:")
            pin_number = input("Enter your PIN:")

            if login(connection, card_number, pin_number):
                print("""
                You have successfully logged in!")
                
                """)
                sub_menu()
                submenu_selection = int(input())
                while submenu_selection != 5:
                    if submenu_selection == 1:
                        check_balance(connection, card_number)
                        sub_menu()
                        submenu_selection = int(input())
                    elif submenu_selection == 2:
                        add_income(connection, card_number)
                        sub_menu()
                        submenu_selection = int(input())
                    elif submenu_selection == 3:
                        do_transfer(connection, card_number, pin_number)
                        sub_menu()
                        submenu_selection = int(input())
                    elif submenu_selection == 4:
                        close_account(connection, card_number, pin_number)
                        sub_menu()
                        submenu_selection = int(input())
                    elif submenu_selection == 5:
                        print("You have successfully logged out!")
                        break
                    elif submenu_selection == 0:
                        print("Bye!")
                        exit = True
                        break
            else:
                print("Wrong card number or PIN!")

        elif menu_selection == 0:
            print("Bye!")
            exit = True
            break
        else:
            menu()


def sub_menu():
    print("""
    1. Balance
    2. Add income
    3. Do transfer
    4. Close account
    5. Log out
    0. Exit
    """"")


connection = sqlite3.connect('card.s3db')
cur = connection.cursor()
cur.execute(CREATE_TABLE)
connection.commit()

menu()
