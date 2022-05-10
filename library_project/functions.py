from PIL import Image
import os
import secrets
from library_project import app


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_image.filename)
    image_filename = random_hex + file_extension
    image_path = os.path.join(app.root_path, 'static/images', image_filename)

    output_size = (300, 300)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_filename



def send_reset_email(user):
    token = user.get_reset_token()

    # msg = Message('Slaptažodžio atnaujinimo užklausa',
    #               sender='o.valioniene.testinis@gmail.com',
    #               recipients=[user.email])
    # msg.body = f'''Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
    # {url_for('reset_token', token=token, _external=True)}
    # Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
    # '''
    # mail.send(msg)