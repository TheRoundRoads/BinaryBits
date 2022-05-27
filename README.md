# BinaryBits
A simple bank prototype website built using flask and sqlite3. It includes a login page, and topup and transaction functions.

There are 3 main pages:
1. Root page, where users can login
2. Sign up page, users register an account with a username and password
3. User page, users can topup their balance, transfer money, or log out. 

There are 2 tables in the database - users and transactions.
"users" contains data on usernames, hashed passwords (md5), and account balances.
"transactions" contains data on datetime the transaction occured, id of sender, id of receiver, and transaction amount.

CSS is pretty bad but this was just a practice for functionality.
