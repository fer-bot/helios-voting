import os
import pymongo

client = pymongo.MongoClient(
    os.getenv('DATABASE_HOST', 'localhost'),
    int(os.getenv('DATABASE_PORT', 27017)))

db = client[os.getenv('DATABASE_NAME', 'helios')]

# indexes for room_voters
db.room_voters.create_index([('room_id', pymongo.ASCENDING)], unique=False)
db.room_voters.create_index(
    [('room_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)

# indexes for room_authorities
db.room_authorities.create_index(
    [('room_id', pymongo.ASCENDING)], unique=False)
db.room_authorities.create_index(
    [('room_id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)

# indexes for room_details
db.room_details.create_index([('room_id', pymongo.ASCENDING)], unique=True)


def room_is_exist(room_id):
    return db.room_details.find_one({'room_id': room_id})


def creator_room_is_accessible(username, room_id):
    room = db.room_details.find_one({'room_id': room_id})
    if not room:
        return

    if room['creator'] != username:
        return

    return room


def room_create_detail(room_detail):
    return db.room_details.insert(room_detail)


def room_update_detail(filter, value):
    return db.room_details.update_one(filter, value)


def room_add_authority(data):
    return db.room_authorities.insert_one(data)


def room_get_authorities(room_id):
    return db.room_authorities.find({'room_id': room_id})


def room_delete_authorithy(query):
    return db.room_authorities.delete_one(query)


def room_get_voters(room_id):
    return db.room_voters.find({'room_id': room_id})


def room_add_voter(data):
    return db.room_voters.insert_one(data)


def room_delete_voter(query):
    return db.room_voters.delete_one(query)


def authority_room_is_accessible(username, room_id):
    return db.room_authorities.find_one(
        {'room_id': room_id, 'user_id': username})


def authority_update_detail(filter, value):
    return db.room_authorities.update_one(filter, value)


def voter_room_is_accessible(username, room_id):
    return db.room_voters.find_one(
        {'room_id': room_id, 'user_id': username})


def voter_update_detail(filter, value):
    return db.room_voters.update_one(filter, value)


def voter_get_voters(room_id):
    return db.room_voters.find({'room_id': room_id})
