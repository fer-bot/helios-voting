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
def authorithy_main(request):
    if request.method == 'GET':
        template = loader.get_template('authorities/main.html')
        return HttpResponse(template.render({}, request))

    if request.method == 'POST':
        try:
            room_id = request.POST["room_id"]
            return redirect(f"/authority/{room_id}")

        except:
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/authority/")


@login_required
def authority_submit(request, room_id):
    if request.method == 'GET':
        try:
            details = DB.authority_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/authority/")

            room = DB.room_is_exist(room_id)

            if not room['is_open']:
                if details['public_key']:
                    template = loader.get_template(
                        'authorities/text_page.html')
                    message = 'You have submitted your public key!'
                    return HttpResponse(template.render({'message': message}, request))
                template = loader.get_template(
                    'authorities/submit_pk.html')
                return HttpResponse(template.render({'room': room, 'details': details}, request))

            if room['is_open'] and not room['is_close']:
                template = loader.get_template(
                    'authorities/text_page.html')
                message = 'Voting event in progress!'
                return HttpResponse(template.render({'message': message}, request))

            if room['is_close'] and not details['decrypt_a']:
                template = loader.get_template('authorities/submit_proof.html')
                return HttpResponse(template.render({'room': room, 'details': details}, request))

            template = loader.get_template(
                'authorities/text_page.html')
            message = 'Thank you for using Helios!'
            return HttpResponse(template.render({'message': message}, request))

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect(f"/authority/")

    if request.method == 'POST':
        try:
            details = DB.authority_room_is_accessible(
                request.user.username, room_id)

            if not details:
                messages.info(
                    request, f'Room is not Accessible!')
                return redirect("/authority/")

            room = DB.room_is_exist(room_id)

            if not room['is_open'] and not details['public_key']:
                pk = request.POST['user_pk']

                filter = {'room_id': room_id, 'user_id': request.user.username}
                newvalues = {"$set": {'public_key': pk}}
                DB.authority_update_detail(filter, newvalues)
                return redirect(f"/authority/{room_id}/")

            if room['is_close'] and not room['is_released'] and not details['decrypt_a']:

                proof_u = int(request.POST['proof_u'])
                proof_v = int(request.POST['proof_v'])
                proof_s = int(request.POST['proof_s'])
                proof_d = int(request.POST['proof_d'])
                cipher = (int(room['total_a']), int(room['total_b']))
                proof = (proof_u, proof_v, proof_s, proof_d)

                is_valid = Helios.CP_check(
                    int(details['public_key']), cipher, proof, int(room['generator']), int(room['prime']))
                if not is_valid:
                    messages.info(request, f'Not Valid! Try again!')
                    return redirect(f"/authority/{room_id}/")

                decrypt_a = Helios.get_ai(proof_d, int(room['prime']))

                filter = {'room_id': room_id, 'user_id': request.user.username}
                newvalues = {"$set": {
                    'decrypt_a': str(decrypt_a),
                    'proof_u': str(proof_u),
                    'proof_v': str(proof_v),
                    'proof_s': str(proof_s),
                    'proof_d': str(proof_d),
                }}

                DB.authority_update_detail(filter, newvalues)
                messages.info(request, f'Proof Submited!')
                return redirect(f"/authority/{room_id}/")

            if room['is_close'] and not room['is_released'] and details['decrypt_a']:
                messages.info(
                    request, f'Failed! You have submited your proof before!')
                redirect(f"/authority/{room_id}/")

            return redirect(f"/authority/{room_id}/")

        except Exception as e:
            print(e)
            messages.info(
                request, f'Oops! Something went wrong! Please try again.')
            return redirect("/authority/")
