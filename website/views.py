from flask import Blueprint, render_template, request, flash, jsonify, redirect,url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Child, History, User
from . import db
import datetime as dt
from time import sleep
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components

views = Blueprint('views', __name__)


@views.route('/', methods=['GET','POST'])
@login_required
def home():
    user = current_user
    def get_kids(user):
        result = Child.query.filter_by(c_parent_id=user).all()
        return result

    data = len(get_kids(user.id))
        
    return render_template('home.html', data=data, user=current_user)


@views.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    user = current_user
    if request.method == 'POST':
        u_name = request.form.get('userName')
        u_fname = request.form.get('firstName')
        u_lname = request.form.get('lastName')
        u_email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(u_email) < 4:
            flash('Email must be greater than 4 chars', category='error')
        elif len(u_fname) < 2:
            flash('First name must be greater than 1 chars', category='error')
        elif password1 != password2:
            flash('Password don\'t match', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 7 characters', category='error')
        elif generate_password_hash(password1, method='sha256') == user.u_password:
            flash('Password is the same as the previous one', category='error')
        else:
            db.session.query(User).filter(User.id == user.id).update({User.u_name:u_name, User.u_fname:u_fname, User.u_lname: u_lname, 
            User.u_email:u_email, User.u_password:generate_password_hash(password1, method='sha256')}, synchronize_session='fetch')
            db.session.commit()
            flash('Account updated!', category='success')
            return redirect(url_for('views.home'))

    return render_template('edit_profile.html', user=user)


@views.route('/add_child', methods=['GET','POST'])
@login_required
def add_child():
    user = current_user
    if request.method == 'POST':
        c_first_name = request.form.get('c_fname')
        c_last_name = request.form.get('c_lname')
        c_birth_date = request.form.get('c_birth_date')
        c_gender = request.form.get('c_gender')
        c_height = request.form.get('c_height')
        c_weight = request.form.get('c_weight')

        def is_numeric_float(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        d = dt.datetime.strptime(c_birth_date, "%Y-%m-%d")
        c_birth_date = d.date()
        child = Child.query.filter_by(c_first_name=c_first_name).first()
        days = (dt.datetime.now() - dt.datetime.strptime(str(c_birth_date), "%Y-%m-%d")).days
        
        if child:
            flash('Child already exists', category='error')
        elif days < 0:
            flash('Cannot add an unborn child', category='error')
        elif not c_height.isnumeric():
            flash('Height must be expressed in cm', category='error')
        elif not is_numeric_float(c_weight):
            flash(f'Weight must be expressed in Kg.grams: {c_weight}', category='error')
        else:
            new_child = Child(c_first_name=c_first_name, c_last_name=c_last_name, c_birth_date=c_birth_date, c_gender=c_gender, c_height=c_height, c_weight=c_weight, c_parent_id=user.id)
            db.session.add(new_child)
            db.session.commit()
            flash('Child added successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template('add_child.html', user=user)


@views.route('/add_measurements', methods=['GET','POST'])
@login_required
def add_measurements():
    user = current_user
    child = Child.query.get(request.args.get('child'))
    if child == None:
        flash('Child does not exist', category='error')
        return redirect(url_for('views.home'))
    elif child.c_parent_id != user.id:
        flash('This child is not yours', category='error')
        return redirect(url_for('views.home'))
    else:
        if request.method == 'POST':
            child_height = request.form.get('child_height')
            child_weight = request.form.get('child_weight')
            date_created = request.form.get('m_date')

            if not child_height:
                flash('Child heigth need to be filled in!', category='error')
            elif not child_weight:
                flash('Child heigth need to be filled in!', category='error')
            elif not date_created:
                date_created = dt.datetime.now().date().strftime('%Y-%m-%d')
            elif (dt.datetime.now() - dt.datetime.strptime(str(date_created), "%Y-%m-%d")).days < 0:
                flash(f'Cannot add data for future dates! Today is {dt.datetime.now().date()} and you are trying to add data for {date_created}', category='error')
            else:
                # convert to date since data is coming in as string
                date_created = dt.datetime.strptime(date_created, "%Y-%m-%d").date()
                
                # calculate week from dateof birth to date_created
                week = abs((dt.datetime.strptime(str(child.c_birth_date), "%Y-%m-%d") - dt.datetime.strptime(str(date_created), "%Y-%m-%d")).days)
                week = (week // 7) + (week % 7 > 0) 
                entry = History(week=week, child_height=int(child_height), child_weight=float(child_weight), date_created=date_created, child_id=child.id)

                db.session.add(entry)
                db.session.commit()

                flash('Measurements added successfully!', category='success')
                return redirect(url_for('views.home'))

    return render_template('add_measurements.html', user=user, child=child)


@views.route('/check_progress', methods=['GET','POST'])
@login_required
def check_progress():
    
    user = current_user
    child = Child.query.get(request.args.get('child'))    
    
    if child == None:
        flash('Child does not exist', category='error')
        return redirect(url_for('views.home'))
    elif child.c_parent_id != user.id:
        flash('This child is not yours', category='error')
        return redirect(url_for('views.home'))
    else:
        dates = []
        weights = []
        heights = []
        weeks = []
        for history in child.history:
            dates.append(history.date_created)
            weights.append(history.child_weight)
            heights.append(history.child_height)
            weeks.append(history.week)

        x = dates # time
        y0 = heights # height
        y1 = weights # weight

        # create a new plot
        p = figure(
            # tools="pan,box_zoom,reset,save",
            # y_axis_type="log",
            x_axis_type='datetime',
            y_range=[min([int(x) for x in weights])-3, max(heights)+10], title=f"{child.c_first_name}'s growth over time",
            x_axis_label='over time', 
            y_axis_label='weeks',
            toolbar_location = "below"
        )

        # add some renderers
        p.line(x, y0,  legend_label="Growth in weight", line_color="cornflowerblue")
        p.circle(x, y0, legend_label="Growth in weight", fill_color="cornflowerblue", line_color="cornflowerblue", size=6)
        p.line(x, y1, legend_label="Growth in height", line_color="indianred")
        p.circle(x, y1, legend_label="Growth in height", fill_color="indianred", line_color="indianred", size=6)
        p.sizing_mode="stretch_width"
        p.legend.location="center_right"
        p.legend.click_policy="hide"

        script, div = components(p)

    return render_template('check_progress.html', user=user, script=script, div=div, child=child)