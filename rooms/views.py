from datetime import datetime
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import loader
import utils.mongodb as DB
import utils.helios as Helios


@login_required
def room_main(request):
    if request.method == 'GET':
        template = loader.get_template('rooms/main.html')
        return HttpResponse(template.render({}, request))

    if request.method == 'POST':
        try:
            room_id = request.POST["room_id"]
            return redirect(f"/room/update/{room_id}/")

        except:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/room/")


@login_required
def room_create(request):
    if request.method == 'GET':
        try:
            template = loader.get_template('rooms/create.html')

            room_id = Helios.generate_room_id()
            while DB.room_is_exist(room_id=room_id):
                room_id = Helios.generate_room_id()
            room_prime = Helios.generate_large_prime()
            room_constant = Helios.find_primitive_root(room_prime)

            room_detail = {
                'room_id': room_id,
                'creator': request.user.username,
                'creation_time': datetime.now(),
                'prime': str(room_prime),
                'generator': str(room_constant),
                'public_key': None,
                'is_locked': None,
                'is_open': None,
                'is_close': None,
                'is_released': None,
                'question': None,
                'answers': None,
                'total_a': None,
                'total_b': None,
                'total_g': None,
                'total_vote': None,
                'number_of_voter': None,
            }

            DB.room_create_detail(room_detail)
            return HttpResponse(template.render(room_detail, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/room/")


@login_required
def room_update_details(request, room_id):
    if request.method == 'GET':
        room = DB.creator_room_is_accessible(request.user.username, room_id)

        if not room:
            messages.info(
                request, f'Room is not Accessible!')
            return redirect("/room/")

        template = loader.get_template('rooms/update_page.html')
        return HttpResponse(template.render(room, request))

    if request.method == 'POST':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_open']:
                messages.info(
                    request, f'Failed! Room is already open!')
                return redirect(f"/room/update/{room_id}")

            qn = request.POST['room_qn']
            ans1 = request.POST['room_ans1']
            ans2 = request.POST['room_ans2']

            filter = {'room_id': room_id}
            newvalues = {"$set": {'question': qn, 'answer': [ans1, ans2]}}
            DB.room_update_detail(filter, newvalues)

            messages.info(
                request, f'Update Successful!')
            return redirect(f'/room/update/{room_id}/')

        except:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}")


@login_required
def room_open(request, room_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if not room['is_locked']:
                messages.info(
                    request, f'Failed! Room is not locked!')
                return redirect(f"/room/update/{room_id}")

            if room['is_open']:
                messages.info(
                    request, f'Failed! Room is already open!')
                return redirect(f"/room/update/{room_id}")

            authorities = [c['public_key']
                           for c in DB.room_get_authorities(room_id)]

            if not all(authorities):
                messages.info(
                    request, f'Failed! One or more authority(s) have not submit their Public key!')
                return redirect(f"/room/update/{room_id}")

            room_pk = str(Helios.get_room_pk(
                [int(pk) for pk in authorities], int(room['prime'])))

            filter = {'room_id': room_id}
            newvalues = {
                "$set": {'is_open': datetime.now(), 'public_key': room_pk}}
            DB.room_update_detail(filter, newvalues)

            messages.info(
                request, f'Update Successful!')
            return redirect(f'/room/update/{room_id}/')

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}")


@login_required
def room_close(request, room_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if not room['is_open']:
                messages.info(
                    request, f'Failed! Room is not open yet!')
                return redirect(f"/room/update/{room_id}")

            if room['is_close']:
                messages.info(
                    request, f'Failed! Room is already closed!')
                return redirect(f"/room/update/{room_id}")

            ciphers = [(int(vote['voting_a']), int(vote['voting_b'])) for vote in DB.voter_get_voters(
                room_id) if vote['voting_a'] and vote['voting_b']]
            total_a, total_b = Helios.add_ciphers(ciphers, int(room['prime']))

            filter = {'room_id': room_id}
            newvalues = {"$set": {
                'is_close': datetime.now(),
                'total_a': str(total_a),
                'total_b': str(total_b),
            }}
            DB.room_update_detail(filter, newvalues)

            messages.info(
                request, f'Update Successful!')
            return redirect(f'/room/update/{room_id}/')

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}")


@login_required
def room_release(request, room_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if not room['is_open']:
                messages.info(
                    request, f'Failed! Room is not open yet!')
                return redirect(f"/room/update/{room_id}")
            if not room['is_close']:
                messages.info(
                    request, f'Failed! Room is not close yet!')
                return redirect(f"/room/update/{room_id}")

            if room['is_released']:
                messages.info(
                    request, f'Failed! Voting result is already released!')
                return redirect(f"/room/update/{room_id}")

            decrypted_ciphers = [detail['decrypt_a']
                                 for detail in DB.room_get_authorities(room_id)]

            if not all(decrypted_ciphers):
                messages.info(
                    request, f'Failed! Some authority(s) have not submit their part!')
                return redirect(f"/room/update/{room_id}")

            decrypted_ciphers = [int(a) for a in decrypted_ciphers]

            total_g = Helios.add_decrypted_ciphers(
                decrypted_ciphers, int(room['total_b']), int(room['prime']))

            vote_result = Helios.decrypt_ciphers(
                total_g, int(room['generator']), int(room['prime']))

            number_of_voter = len([v for v in DB.voter_get_voters(
                room_id) if v['voting_a'] and v['voting_b']])

            filter = {'room_id': room_id}
            newvalues = {"$set": {
                'is_released': datetime.now(),
                'total_g': str(total_g),
                'total_vote': str(vote_result),
                'number_of_voter': str(number_of_voter),
            }}
            print(newvalues)
            DB.room_update_detail(filter, newvalues)

            print(newvalues)

            messages.info(
                request, f'Update Successful!')
            return redirect(f'/room/update/{room_id}/')

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}")


@ login_required
def room_update_authority(request, room_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            authorities = [c for c in DB.room_get_authorities(room_id)]

            data = {
                'room_id': room_id,
                'authorities': authorities,
                'is_locked': bool(room['is_locked']),
            }
            template = loader.get_template('rooms/update_authority.html')
            return HttpResponse(template.render(data, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/")

    if request.method == 'POST':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_locked']:
                messages.info(
                    request, f'Room is already locked!')
                return redirect(f"/room/update/{room_id}/authority/")

            user_id = request.POST['username']

            new_authority = {
                'room_id': room_id,
                'user_id': user_id,
                'public_key': None,
                'decrypt_a': None,
                'proof_u': None,
                'proof_v': None,
                'proof_s': None,
                'proof_d': None,
            }
            DB.room_add_authority(new_authority)
            messages.info(
                request, f'Adding new authority successfull!')
            return redirect(f"/room/update/{room_id}/authority/")

        except Exception as e:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/authority/")


@ login_required
def room_delete_authority(request, room_id, user_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_locked']:
                messages.info(
                    request, f'Room is already locked!')
                return redirect(f"/room/update/{room_id}/authority/")

            DB.room_delete_authorithy({'room_id': room_id, 'user_id': user_id})
            messages.info(
                request, f'Deletion Successful!')
            return redirect(f"/room/update/{room_id}/authority/")

        except Exception as e:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/authority/")


@ login_required
def room_update_lock(request, room_id):
    if request.method == 'POST':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_locked']:
                messages.info(
                    request, f'Room is already locked!')
                return redirect(f"/room/update/{room_id}/authority/")

            filter = {'room_id': room_id}
            newvalues = {"$set": {'is_locked': datetime.now()}}
            DB.room_update_detail(filter, newvalues)

            messages.info(
                request, f'Successfully locking the room!')
            return redirect(f"/room/update/{room_id}/authority/")

        except Exception as e:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/authority/")


@ login_required
def room_update_voter(request, room_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            voters = [c for c in DB.room_get_voters(room_id)]

            data = {
                'room_id': room_id,
                'voters': voters,
                'is_close': room['is_close']
            }
            template = loader.get_template('rooms/update_voter.html')
            return HttpResponse(template.render(data, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/")

    if request.method == 'POST':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_close']:
                messages.info(
                    request, f'Voting is already closed!')
                return redirect(f"/room/update/{room_id}/voter/")

            user_id = request.POST['username']
            new_voter = {
                'room_id': room_id,
                'user_id': user_id,
                'voting_time': None,
                'voting_a': None,
                'voting_b': None,
                'proof_a0': None,
                'proof_a1': None,
                'proof_b0': None,
                'proof_b1': None,
                'proof_c0': None,
                'proof_c1': None,
                'proof_r0': None,
                'proof_r1': None,
            }
            DB.room_add_voter(new_voter)
            messages.info(
                request, f'Adding new voter successfull!')
            return redirect(f"/room/update/{room_id}/voter/")

        except Exception as e:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/voter/")


@ login_required
def room_delete_voter(request, room_id, user_id):
    if request.method == 'GET':
        try:
            room = DB.creator_room_is_accessible(
                request.user.username, room_id)

            if not room:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/room/")

            if room['is_close']:
                messages.info(
                    request, f'Voting is already closed!')
                return redirect(f"/room/update/{room_id}/voter/")

            DB.room_delete_voter({'room_id': room_id, 'user_id': user_id})
            messages.info(
                request, f'Deletion Successful!')
            return redirect(f"/room/update/{room_id}/voter/")

        except Exception as e:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/room/update/{room_id}/voter/")
