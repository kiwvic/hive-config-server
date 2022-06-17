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
5. Run server