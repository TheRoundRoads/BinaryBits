# https://trello.com/b/YppiVjHf/binarybits

import sqlite3
from flask import Flask, render_template, request, redirect
import hashlib
import datetime

# Start connection to sqlite server
def get_db_connection():
    conn = sqlite3.connect('databases/db.sqlite')
    return conn, conn.cursor()

# MD5 hash for password
def hashMD5(password):
    return hashlib.md5(password.encode()).hexdigest()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def user():
    if request.method == 'POST': # Login by form
        name, pw = request.form.get("username"), request.form.get("password")
        conn, cursor = get_db_connection()
        
        result = cursor.execute("SELECT id, BALANCE FROM users WHERE username = ? AND password = ?", (name, hashMD5(pw)))
        result = list(result)
        # Check if user exists
        if len(result) > 0:    
            account, balance = result[0][0], result[0][1]    
                     
            # Update balance
            topup = request.form.get("topup")
            balanceError = ""   
            if topup != None:
                topup = int(topup)
                if 0 <= topup <= 2000:  # Check for valid topup amount
                    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance + topup, account))
                    conn.commit()
                    balance += topup
                else:
                    balanceError = "Invalid topup amount."
            
            # Transactions
            formData = [request.form.get("otherUser"), request.form.get("transactionAmount"), request.form.get("checkPassword")]
            
            transactionError = ""
            
            # Check if transaction form was submitted
            if request.form.get("transaction") != None:
                # Check if user exists - Might be vulnerability?
                x = cursor.execute("SELECT id, balance FROM users WHERE username=?", (formData[0],))
                x = list(x)
                if len(x) == 0:
                    transactionError = "Invalid user entered"
                else:
                    otherAccount, otherBalance = x[0][0], x[0][1]
                
                # Check if amount entered, and if it is within the range, and not more than balance 
                amount = formData[1]
                if amount == None:
                    transactionError = "Amount not entered"
                elif int(amount) > balance:
                    transactionError = f"Not enough money, missing {int(amount) - balance}"
                elif 0 < int(amount) <= 2000:
                    amount = int(amount)
                else:
                    transactionError = "Invalid amount entered"
                        
                # Check if password entered matches account password
                pw1 = formData[2]
                if pw1 != pw:
                    transactionError = "Password entered wrongly"
                
                # Update both sender's and receiver's balance, as well as transactions table
                if transactionError == "":
                    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance - amount, account))
                    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (otherBalance + amount, otherAccount))
                    cursor.execute("INSERT INTO transactions (datetime, sender, receiver, amount) VALUES (?, ?, ?, ?)",
                                   (str(datetime.datetime.now())[:19], account, otherAccount, amount))
                    conn.commit()
                    balance -= amount
            
            # Choose what data to retain on the form after submission     
            for i, ele in enumerate(formData):
                if ele == None or transactionError == "":
                    formData[i] = ""
                    
            # Get 5 most recent transactions for sent and received
            selections_sent = list(cursor.execute("SELECT * FROM transactions WHERE sender=? ORDER BY datetime DESC LIMIT 5", (account,)))
            sent = []
            for i, selection in enumerate(selections_sent):
                receiver = list(cursor.execute("SELECT username FROM users WHERE id=?", (selection[3],)))[0][0]
                sent.append((selection[1], name, receiver, selection[4]))
                
            selections_received = list(cursor.execute("SELECT * FROM transactions WHERE receiver=? ORDER BY datetime DESC LIMIT 5", (account,)))
            received = []
            for i, selection in enumerate(selections_received):
                sender = list(cursor.execute("SELECT username FROM users WHERE id=?", (selection[2],)))[0][0]
                received.append((selection[1], sender, name, selection[4]))
            
            
            return render_template("login.html",
                                    username=name, password=pw, 
                                    account=account, balance=balance,
                                    balanceError=balanceError,
                                    transactionError=transactionError,
                                    formData=formData,
                                    sent=sent, received=received)
            
        else:
            return render_template("index.html", error="Invalid username or password",
                                   username=name, password=pw)
    
    return redirect("/")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'GET':
        return render_template("signup.html")

    else:
        # Get username, password and confirmed password from form
        name, pw1, pw2 = request.form.get("username"), request.form.get("password"), request.form.get("confirm")
        conn, cursor = get_db_connection()
        
        x = cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
        # Check if user already exists
        if len(list(x)) > 0:
            return render_template("signup.html", message1="Sorry, that username is taken.",
                                   username=name, password=pw1, confirm=pw2)
        
        # Check for secure password
        elif len(pw1) < 8:
            return render_template("signup.html", message2="Password must be at least 8 characters.",
                                   username=name, password=pw1, confirm=pw2)
        
        # Check if confirmed password is correct
        elif pw1 != pw2:
            return render_template("signup.html", message3="Please check that the password is keyed in correctly.",
                                   username=name, password=pw1, confirm=pw2)
        
        # Insert new user into users table
        else:
            cursor.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, 0)", (name, hashMD5(pw1)))
            conn.commit()
            return render_template("success_signup.html")

if __name__ == '__main__':
    app.run()