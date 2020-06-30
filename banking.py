from random import sample
from string import digits
from sys import exit
import sqlite3


class Bank:
    conn = sqlite3.connect("card.s3db")
    c = conn.cursor()
#     c.execute("""CREATE TABLE card (
# 	id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 	number	TEXT,
# 	pin	TEXT,
# 	balance	INTEGER DEFAULT 0
# )""")
#     conn.commit()

    def __init__(self):
        self.card_num = ""
        self.pin = ""
        self.balance = 0

    def luhn(self, card_num):
        c = [int(x) for x in card_num]
        c_ = []
        c2 = []
        total = 0
        x = 1
        for i in c:
            if x % 2 != 0:
                c_.append(i * 2)
            else:
                c_.append(i)
            x += 1

        for i in c_:
            if i > 9:
                c2.append(i - 9)
            else:
                c2.append(i)

        for i in c2:
            total += i

        for i in range(10):
            if (total + i) % 10 == 0:
                c.append(i)

        y = ""
        for i in c:
            y += str(i)
        return y
    def luhn_check(self,num):
        c = [int(x) for x in num]
        last = c.pop()
        c_ = []
        c2 = []
        total = 0
        x = 1
        for i in c:
            if x % 2 != 0:
                c_.append(i * 2)
            else:
                c_.append(i)
            x += 1

        for i in c_:
            if i > 9:
                c2.append(i - 9)
            else:
                c2.append(i)

        for i in c2:
            total += i

        for i in range(10):
            if (total + i) % 10 == 0:
                c.append(i)
        if c[len(c)-1] == last:
            return True

    def create_account(self):
        luhn_num = "400000" + "".join(sample(digits, 9))
        self.card_num = Bank.luhn(self, luhn_num)
        print(f"""Your card has been created
Your card number:
{self.card_num}""")

        self.pin = "".join(sample(digits, 4))
        print(f"""Your card PIN:
{self.pin}\n""")
        param = [self.card_num, self.pin]
        self.c.execute('INSERT INTO card(number,pin) VALUES(?,?)', param)
        self.conn.commit()

    def add(self,inp,param):
        para = [inp, param[0]]
        self.c.execute("UPDATE card SET balance = balance + ? WHERE number= ? ", para)
        self.conn.commit()
    def transfer(self,inp,param):
        inp = [inp]
        self.c.execute("SELECT number FROM card where number= ?", inp)
        number = self.c.fetchone()
        if inp == [param[0]]:
            print("You can't transfer money to the same account!")
        elif not Bank.luhn_check(self, *inp):
            print("Probably you made mistake in the card number. Please try again!")
        elif number is not None:
            i = int(input("Enter how much money you want to transfer:\n"))
            self.c.execute("SELECT balance FROM card WHERE number = ?", [param[0]])
            balance = self.c.fetchone()
            balance_ = 0
            for b in balance:
                balance_ = int(b)
            if i > balance_:
                print("Not enough money!")
            else:
                para = [i, param[0]]
                self.c.execute("UPDATE card SET balance = balance - ? WHERE number= ?", para)
                Bank.add(self, i, inp)
                self.conn.commit()
                print("Success!")
        else:
            print("Such a card does not exist!")


    def close_account(self,param):
        self.c.execute("DELETE FROM card where number= ?", [param[0]])
        self.conn.commit()
        print("The account has been closed!")
    def login_ops(self, param):
        while True:
            state = input(f"""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")

            self.c.execute("SELECT balance FROM card where number=? AND pin=?", param)
            balance = self.c.fetchone()
            if state == "1":
                print("Balance:", str(balance).strip("(),"), "\n")
            elif state == "2":
                i = int(input("Enter income:\n"))
                Bank.add(self, i, param)
                print("Income was added!")

            elif state == "3":
                i = input("""Transfer
Enter card number:
""")
                Bank.transfer(self,i,param)
            elif state == "4":
                Bank.close_account(self,param)
                break
            elif state == "5":
                print("You have successfully logged out!\n")
                break
            elif state == "0":
                print("Bye!\n")
                self.conn.close()
                exit()

    def login_account(self):
        card_input = input("Enter your card number:\n")
        pin_input = input("Enter your PIN:\n")
        param = [card_input, pin_input]
        self.c.execute("SELECT number FROM card WHERE number=? AND pin=?", param)
        result = self.c.fetchone()
        if result is None:
            print("Wrong card number or PIN!\n")

        elif result is not None:
            print("You have successfully logged in!\n")
            Bank.login_ops(self, param)

    def state_machine(self, state):
        while True:
            state = input(f"""1. Create an account
2. Log into account
0. Exit
""")
            if state == "1":
                Bank.create_account(self)
            elif state == "2":
                Bank.login_account(self)

            elif state == "0":
                print("Bye!")
                self.conn.close()
                break


b = Bank()
b.state_machine("")
