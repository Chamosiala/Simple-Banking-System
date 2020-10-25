import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
                id INTEGER, 
                number TEXT, 
                pin TEXT, 
                balance INTEGER DEFAULT 0
                );""")
conn.commit()

logged_in = False
found = 0


class CreditCard:
    registered_numbers = []
    balance = 0

    def __init__(self):
        self.number = '400000' + str(random.randint(100000000, 999999999))
        self.pin = random.randint(1000, 9999)
        self.number += CreditCard.checksum(self)
        CreditCard.registered_numbers.append(self.number)

    def checksum(self):
        cnumber = self.number
        counter = 1
        digitsum = 0
        for digit in cnumber:
            if counter % 2 != 0:
                digit = int(digit) * 2
            if int(digit) > 9:
                digit = int(digit) - 9
            digitsum += int(digit)
            counter += 1
        if digitsum % 10 == 0:
            return '0'
        else:
            return str(10 - digitsum % 10)


def checksum(card_number):
    counter = 1
    digitsum = 0
    for digit in card_number[:15]:
        if counter % 2 != 0:
            digit = int(digit) * 2
        if int(digit) > 9:
            digit = int(digit) - 9
        digitsum += int(digit)
        counter += 1
    if digitsum % 10 == 0:
        return '0'
    else:
        return str(10 - digitsum % 10)


running = True
while running:
    choice = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if choice == '1':
        card = CreditCard()
        cur.execute(f"""INSERT INTO card (number, pin) VALUES ({card.number}, {card.pin});""")
        conn.commit()
        print(f"Your card has been created\nYour card number:\n{card.number}\nYour card PIN:\n{card.pin}\n")
    
    elif choice == '2':
        login_number = input("\nEnter your card number:\n")
        login_pin = input("Enter your PIN:\n")

        for row in cur.execute("SELECT * FROM card;"):
            if login_number == row[1] and login_pin == row[2]:
                logged_in = True
                print("You have successfully logged in!")
                balance = row[3]
                while 1:
                    login_choice = input("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close Account\n5. Log out\n0."
                                         " Exit\n")
                    
                    if login_choice == '1':
                        print('\nBalance: ', balance)
                    
                    elif login_choice == '2':
                        income = int(input("Enter income:\n"))
                        cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {login_number};")
                        conn.commit()
                        balance += income
                        print("Income was added!")
                    
                    elif login_choice == '3':
                        print("Transfer")
                        transfer_number = input("Enter card number:\n")
                        
                        if len(transfer_number) == 16 and transfer_number[15] == checksum(transfer_number):
                            for number in cur.execute("SELECT number FROM card;"):
                                
                                if transfer_number == number[0]:
                                    found = 1
                                    
                                    if transfer_number != login_number:
                                        transfer_money = int(input("Enter how much money you want to transfer:\n"))
                                        
                                        if transfer_money > balance:
                                            print("Not enough money!")
                                        else:
                                            cur.execute(f"""UPDATE card 
                                                            SET balance = balance + {transfer_money} 
                                                            WHERE number = {transfer_number};""")
                                            cur.execute(f"""UPDATE card
                                                            SET balance = balance - {transfer_money}
                                                            WHERE number = {login_number};""")
                                            conn.commit()
                                            balance -= transfer_money
                                    else:
                                        print("You can't transfer money to the same account!")
                            if not found:
                                 print("Such a card does not exist.")
                        else:
                            print("Probably you made a mistake in the card number. Please try again!")
                    
                    elif login_choice == '4':
                        cur.execute(f"DELETE FROM card WHERE number = {login_number}")
                        conn.commit()
                        print("The account has been closed!")
                    
                    elif login_choice == '5':
                        print('\nYou have successfully logged out!\n')
                        break
                    
                    elif login_choice == '0':
                        print('\nBye!')
                        running = False
                        break
        if not logged_in:
            print('Wrong card number or PIN!\n')
    
    elif choice == '0':
        print('\nBye!')
        running = False
