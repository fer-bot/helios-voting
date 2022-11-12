## Getting Started

1. make sure you have `python3` and `pip` installed
1. make sure you have a running `mongoDB` cluster
1. type `python3 -m pip install -r requirements.txt` to install dependencies
1. type `python3 -m pip list ` to check installed libraries
1. create a file named `.env` on the root directory of the project
1. run `python manage.py migrate` for admin migration
1. run `python manage.py createsuperuser` and create superuser username and password
1. type `python3 manage.py runserver` to run django server

## Creating super user

## Adding New Dependencies

1. type `python3 -m pip install <your-new-dependency>`
1. add the new dependacy to `requirements.txt`

## Env File

Create `.env` file

```
DATABASE_TYPE=mongodb
DATABASE_ENGINE=djongo
DATABASE_HOST=localhost
DATABASE_PORT=27017
DATABASE_NAME=helios

CRYPTO_PRIME_LENGTH=1024
ROOM_ID_LENGTH=8
```
