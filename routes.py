import requests
from flask import render_template, url_for, flash, redirect, request, jsonify
from app import app, db, bcrypt
from forms import RegistrationForm, LoginForm, MatchForm, SearchUserForm
from models import User, Match, Feedback, Friendship
from flask_login import login_user, current_user, logout_user, login_required
from social_api_client import get_user, search_users
from datetime import datetime, timedelta

# Considera mover esto a un archivo de configuración
API_URL = "http://localhost:5002"


@app.route("/")
def index():
    return redirect(url_for('home'))


@app.route("/home")
def home():
    matches = Match.query.all()
    return render_template('match_list.html', matches=matches)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            fecha_nacimiento=form.fecha_nacimiento.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/match/new", methods=['GET', 'POST'])
@login_required
def new_match():
    form = MatchForm()

    # Obtener los amigos del usuario actual
    friends = User.query.join(Friendship, (Friendship.friend_id == User.id)).filter(
        Friendship.user_id == current_user.id).all()

    if form.validate_on_submit():
        match = Match(
            title=form.title.data,
            date=form.date.data,
            location=form.location.data,
            organizer=current_user
        )
        db.session.add(match)
        db.session.commit()

        flash('Partido creado exitosamente. Ahora puedes añadir jugadores.', 'success')
        return redirect(url_for('edit_match', match_id=match.id))

    return render_template('create_match.html', title='Crear Partido', form=form, friends=friends)


@app.route("/match/join/<int:match_id>")
@login_required
def join_match(match_id):
    match = Match.query.get_or_404(match_id)
    if len(match.players) < 10:
        match.players.append(current_user)
        db.session.commit()
        flash('You have joined the match!', 'success')
    else:
        flash('This match is already full.', 'danger')
    return redirect(url_for('home'))


@app.route("/match/cancel/<int:match_id>", methods=['POST'])
@login_required
def cancel_match(match_id):
    match = Match.query.get_or_404(match_id)
    if match.organizer != current_user:
        flash('You do not have permission to cancel this match.', 'danger')
        return redirect(url_for('home'))
    db.session.delete(match)
    db.session.commit()
    flash('The match has been canceled.', 'success')
    return redirect(url_for('home'))


@app.route("/match/edit/<int:match_id>", methods=['GET', 'POST'])
@login_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    if match.organizer != current_user:
        flash('No tienes permiso para editar este partido.', 'danger')
        return redirect(url_for('home'))

    form = MatchForm(obj=match)
    friends = User.query.join(Friendship, (Friendship.friend_id == User.id)).filter(
        Friendship.user_id == current_user.id).all()

    if form.validate_on_submit():
        match.title = form.title.data
        match.date = form.date.data
        match.location = form.location.data
        db.session.commit()
        flash('El partido ha sido actualizado.', 'success')
        return redirect(url_for('home'))

    return render_template('edit_match.html', title='Editar Partido', form=form, match=match, friends=friends)


@app.route("/match/add_player/<int:match_id>/<int:player_id>", methods=['POST'])
@login_required
def add_player_to_match(match_id, player_id):
    match = Match.query.get_or_404(match_id)
    player = User.query.get_or_404(player_id)

    if current_user != match.organizer:
        return jsonify({"success": False, "message": "No tienes permiso para modificar este partido"}), 403

    if player in match.players:
        return jsonify({"success": False, "message": "Este jugador ya está en el partido"}), 400

    match.players.append(player)
    db.session.commit()

    return jsonify({"success": True, "message": f"{player.username} ha sido añadido al partido"})


@app.route("/match/remove_player/<int:match_id>/<int:user_id>", methods=['POST'])
@login_required
def remove_player(match_id, user_id):
    match = Match.query.get_or_404(match_id)
    user = User.query.get_or_404(user_id)
    if match.organizer != current_user:
        flash('You do not have permission to edit this match.', 'danger')
        return redirect(url_for('home'))
    if user in match.players:
        match.players.remove(user)
        db.session.commit()
        flash(f'{user.username} removed from the match.', 'success')
    else:
        flash(f'{user.username} is not in the match.', 'warning')
    return redirect(url_for('edit_match', match_id=match_id))


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user_data = get_user(user_id)
    if user_data is not None:
        return render_template('user_profile.html', user=user_data)
    else:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('home'))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_users(query)
    if results is not None:
        return render_template('search_results.html', results=results, query=query)
    else:
        flash('Error en la búsqueda', 'error')
        return redirect(url_for('home'))


@app.route("/search_friends", methods=['GET', 'POST'])
@login_required
def search_friends():
    form = SearchUserForm()
    if form.validate_on_submit():
        search_term = form.search.data
        users = User.query.filter(
            (User.username.like(f'%{search_term}%')) |
            (User.email.like(f'%{search_term}%'))
        ).all()
        return render_template('search_results.html', users=users)
    return render_template('search_friends.html', form=form)


@app.route("/add_friend/<int:user_id>", methods=['POST'])
@login_required
def add_friend(user_id):
    user_to_add = User.query.get_or_404(user_id)
    if user_to_add == current_user:
        flash('No puedes añadirte a ti mismo como amigo.', 'warning')
    elif Friendship.query.filter_by(user_id=current_user.id, friend_id=user_to_add.id).first():
        flash('Este usuario ya es tu amigo.', 'info')
    else:
        friendship = Friendship(user_id=current_user.id,
                                friend_id=user_to_add.id)
        db.session.add(friendship)
        db.session.commit()
        flash(f'Has añadido a {user_to_add.username} como amigo.', 'success')
    return redirect(url_for('search_friends'))


@app.route("/my_friends")
@login_required
def my_friends():
    friends = User.query.join(Friendship, (Friendship.friend_id == User.id)).filter(
        Friendship.user_id == current_user.id).all()
    return render_template('my_friends.html', friends=friends)


@app.route('/users')
def users():
    users_data = User.query.all()  # Obtiene todos los usuarios de la base de datos
    return render_template('users.html', users=users_data)


def get_availability(cancha_id, start_date, end_date):
    url = "http://localhost:5002/api/availability"

    params = {
        "cancha_id": cancha_id,
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        app.logger.error(f"Error: {response.status_code}")
        app.logger.error(response.json())
        return None


def get_current_week_dates():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")


@app.route('/availability')
def availability():
    return render_template('availability.html')


@app.route('/check_availability', methods=['POST'])
def check_availability():
    cancha_id = request.form.get('cancha_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    availability = get_availability(cancha_id, start_date, end_date)

    if availability is None:
        return jsonify({"error": "No se pudo obtener la disponibilidad"}), 500

    return jsonify(availability)


@app.route('/create_reservation', methods=['POST'])
def create_reservation():
    data = request.form.to_dict()
    response = requests.post(f"{API_URL}/api/reservations", json=data)
    if response.status_code == 201:
        flash('Reserva creada con éxito', 'success')
    else:
        flash('Error al crear la reserva', 'error')
    return redirect(url_for('check_availability'))


@app.route('/delete_reservation/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    response = requests.delete(f"{API_URL}/api/reservations/{reservation_id}")
    if response.status_code == 200:
        flash('Reserva eliminada con éxito', 'success')
    else:
        flash('Error al eliminar la reserva', 'error')
    return redirect(url_for('check_availability'))


@app.route('/provide_feedback/<int:match_id>', methods=['GET', 'POST'])
@login_required
def provide_feedback(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user != match.organizer:
        flash('No tienes permiso para proporcionar retroalimentación para este partido.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        for player in match.players:
            feedback = Feedback(
                match_player_user_id=player.id,
                match_player_match_id=match.id,
                evaluator_id=current_user.id,
                talent_score=request.form.get(f'talent_{player.id}'),
                commited_score=request.form.get(f'committed_{player.id}'),
                friendliness=request.form.get(f'friendliness_{player.id}')
            )
            db.session.add(feedback)
        db.session.commit()
        flash('Retroalimentación enviada con éxito', 'success')
        return redirect(url_for('home'))

    return render_template('provide_feedback.html', match=match)