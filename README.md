# How to

run server: `python manage.py runserver ***.***.***.***:PORT`

init database: 
`python manage.py makemigrations`,
`python manage.py migrate`

re-init database:
1. `Delete the db.sqlite3 file`
2. `Delete all the migrations folder inside all the Django applications`
3. `python manage.py makemigrations`,
`python manage.py migrate`
