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
def voter_main(request):
    if request.method == 'GET':
        template = loader.get_template('voters/main.html')
        return HttpResponse(template.render({}, request))

    if request.method == 'POST':
        try:
            room_id = request.POST["room_id"]
            return redirect(f"/voter/{room_id}/")

        except:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/voter/")


@login_required
def voter_choice(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)
            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                template = loader.get_template(
                    'voters/text_page.html')
                message = 'Voting event is not open yet!'
                return HttpResponse(template.render({'message': message}, request))

            template = loader.get_template('voters/choice.html')
            return HttpResponse(template.render(room, request))
        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/voter/")


@login_required
def voter_vote(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                messages.info(request, 'Voting event is not open yet!')
                return redirect(f"/voter/{room_id}/")
            if room['is_close']:
                messages.info(request, 'Voting event is already closed!')
                return redirect(f"/voter/{room_id}/")

            if details['voting_time']:
                messages.info(request, 'You have voted!')
                return redirect(f"/voter/{room_id}/")

            template = loader.get_template('voters/submit_vote.html')
            return HttpResponse(template.render({'room': room, 'details': details}, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/voter/{room_id}/")
    if request.method == 'POST':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                messages.info(request, 'Voting event is not open yet!')
                return redirect(f"/voter/{room_id}/")
            if room['is_close']:
                messages.info(request, 'Voting event is already closed!')
                return redirect(f"/voter/{room_id}/")

            if details['voting_time']:
                messages.info(request, 'You have voted!')
                return redirect(f"/voter/{room_id}/")

            p = int(room["prime"])
            g = int(room["generator"])
            pk = int(room["public_key"])

            a = int(request.POST['vote_a'])
            b = int(request.POST['vote_b'])

            a0 = int(request.POST['proof_a0'])
            a1 = int(request.POST['proof_a1'])
            b0 = int(request.POST['proof_b0'])
            b1 = int(request.POST['proof_b1'])
            c0 = int(request.POST['proof_c0'])
            c1 = int(request.POST['proof_c1'])
            r0 = int(request.POST['proof_r0'])
            r1 = int(request.POST['proof_r1'])

            if not all([a, b, a0, a1, b0, b1, c0, c1, r0, r1]):
                messages.info(
                    request, f'Not Valid! Some data are empty!')
                return redirect(f"/voter/{room_id}/vote")

            if not Helios.DCP_check([a, b, a0, a1, b0, b1, c0, c1, r0, r1], pk, g, p):
                messages.info(
                    request, f'Not Valid! Try again!')
                return redirect(f"/voter/{room_id}/vote")

            filter = {'room_id': room_id, 'user_id': request.user.username}
            newvalues = {"$set": {
                'voting_time': datetime.now(),
                'voting_a': str(a),
                'voting_b': str(b),
                'proof_a0': str(a0),
                'proof_a1': str(a1),
                'proof_b0': str(b0),
                'proof_b1': str(b1),
                'proof_c0': str(c0),
                'proof_c1': str(c1),
                'proof_r0': str(r0),
                'proof_r1': str(r1),
            }}

            DB.voter_update_detail(filter, newvalues)

            messages.info(
                request, f'Vote is successfull!')
            return redirect(f"/voter/{room_id}/vote")

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/voter/{room_id}/vote")


@login_required
def voter_view_voters(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                messages.info(request, 'Voting event is not open yet!')
                return redirect(f"/voter/{room_id}/")

            voters = [v for v in DB.voter_get_voters(room_id)]

            template = loader.get_template('voters/voters.html')
            return HttpResponse(template.render({'room': room, 'voters': voters}, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/voter/{room_id}/")


@login_required
def voter_view_authorities(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                messages.info(request, 'Voting event is not open yet!')
                return redirect(f"/voter/{room_id}/")

            authorities = [v for v in DB.room_get_authorities(room_id)]

            template = loader.get_template('voters/authorities.html')
            return HttpResponse(template.render({'room': room, 'auths': authorities}, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/voter/{room_id}/")


@login_required
def voter_voting_result(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.voter_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/voter/")

            room = DB.room_is_exist(room_id)

            if not room['is_released']:
                messages.info(request, 'Voting result is not released yet!')
                return redirect(f"/voter/{room_id}/")

            room['choose_1'] = room['total_vote']
            room['choose_0'] = int(
                room['number_of_voter']) - int(room['choose_1'])

            template = loader.get_template('voters/result.html')
            return HttpResponse(template.render(room, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/voter/{room_id}/")
