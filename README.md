# How to

#### run server: 
`python3 manage.py runserver ***.***.***.***:PORT`

#### init database: 
1. `python3 manage.py makemigrations`
2. `python3 manage.py migrate`

#### re-init database:
1. `Delete the db.sqlite3 file`
2. `Delete all the migrations folder inside all the Django applications`
3. `python3 manage.py makemigrations`,
`python3 manage.py migrate`

#### remove all data from tables:
`python3 manage.py flush`

# Setup
1. In 'main' dir create .env file by .env.example
2. Configure 'main/config.json'
3. install dependencies: ```pip3 install -r requirements.txt```
4. Init database
5. ```chmod +x runserver.sh```
6. ```./runserver.sh```

# Error codes
Err value | Error code | Meaning
--- | --- | ---
-1 | NO_REQUESTS | Rig has not sent requests since last time some amount of time
-2 | NO_COIN | Rig has unsupported coin
-3 | ALGT5 | Average Load > 5
-4 | MAINT_MODE | Maintenance mode turned on
-5 | MINER_TURNED_OFF | miner off
