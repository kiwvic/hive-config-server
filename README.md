# How to

#### run server: 
`python manage.py runserver ***.***.***.***:PORT`

#### init database: 
1. `python manage.py makemigrations`
2. `python manage.py migrate`

#### re-init database:
1. `Delete the db.sqlite3 file`
2. `Delete all the migrations folder inside all the Django applications`
3. `python manage.py makemigrations`,
`python manage.py migrate`

#### remove all data from tables:
`python manage.py flush`

# Setup
1. In 'main' dir create .env file by .env.example
2. Configure 'main/config.json'
3. install dependencies: ```pip install -r requirements.txt```
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