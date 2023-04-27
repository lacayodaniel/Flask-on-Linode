from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import sha256_crypt

from flask_app import app, db
from flask_app.models import User, Post
from flask_app.forms import PostForm

import csv
import pandas as pd
import time
import numpy as np

@app.route("/")
def index():
    db.create_all()
    posts = Post.query.all()
    return render_template("index.html", posts=posts)



@app.route("/about")
def about():
    return render_template("index.html")



@app.route("/register", methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    else:
        # Create user object to insert into SQL
        passwd1 = request.form.get('password1')
        passwd2 = request.form.get('password2')

        if passwd1 != passwd2 or passwd1 == None:
            flash('Password Error!', 'danger')
            return render_template('register.html')

        hashed_pass = sha256_crypt.encrypt(str(passwd1))

        new_user = User(
            username=request.form.get('username'),
            email=request.form.get('username'),
            password=hashed_pass)

        if user_exsists(new_user.username, new_user.email):
            flash('User already exsists!', 'danger')
            return render_template('register.html')
        else:
            # Insert new user into SQL
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            flash('Account created!', 'success')
            return redirect(url_for('index'))


@app.route('/redirect/', methods = ['GET', 'POST'])
def weeee():
    email_2 = request.form.get('column')
    data = [1, email_2]
    #df_move = pd.read_csv('./pain.csv')

    with open('./pain.csv', 'a') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        
        write.writerow(data)

    return redirect(url_for('getMove'))



@app.route('/c4b/showMove', methods = ['GET', 'POST'])
def showMove():
    df_move = pd.read_csv('./pain.csv')
    return render_template('showMove.html', move = df_move['Column'].iloc[-1])



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        username = request.form.get('username')
        password_candidate = request.form.get('password')

        # Query for a user with the provided username
        result = User.query.filter_by(username=username).first()

        # If a user exsists and passwords match - login
        if result is not None and sha256_crypt.verify(password_candidate, result.password):

            # Init session vars
            login_user(result)
            flash('Logged in!', 'success')
            return redirect(url_for('index'))

        else:
            flash('Incorrect Login!', 'danger')
            return render_template('login.html')


@app.route('/c4b/start', methods = ['GET', 'POST'])
def start():
    titles = ['Player', 'Column']
    fill = [0,0] # this may be unnecessary
    # 'w' call rewrite the file each time, so all past entries will be deleted
    # pain.csv has the turn and column, however considering changing this to player
    
    with open('./pain.csv', 'w') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        
        write.writerow(titles)
        write.writerow(fill)

    string = ''
    for i in range(42):
        string += str(0)

    with open('./gamestate.csv', 'w') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(['Player', 'Gamestate'])
        write.writerow(['0', string])

    # check if existing sql-alchemy db w/ name "game"
    # if it exists destroy it
    # then make a new db under name game, with ['turn', 'move',]
    return (redirect(url_for('getMove')))


@app.route('/c4b/makemove', methods = ['GET', 'POST'])
def getMove():
    while (1 == int(pd.read_csv('pain.csv')['Player'].iloc[-1])):
        # while == 1 means the remote player made the most recent move
        time.sleep(3) # average time to make a move
        # print("sleep")
        continue

    f = pd.read_csv("gamestate.csv", dtype=str)
    game = str(f['Gamestate'].iloc[-1])
    gamestate = []
    for row in np.ndarray.tolist(make_board(game)):
        gamestate.append(' '.join(row))

    fill = [0,0] # this may be unnecessary
    # 'w' call rewrite the file each time, so all past entries will be deleted
    # pain.csv has the turn and column, however considering changing this to player
    
    with open('./gamestate.csv', 'a') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(fill)
    
    return render_template('connect4.html', game = gamestate)


def make_board(game):
    gamestate = np.zeros((6,7),dtype=np.str_)
    print(gamestate)
    j=0
    l=0
    print(game)
    print(type(game))
    for i in range(42): # total rows
        # gamestate[j][l] = int(game[i])
        if game[i] == "2":
            gamestate[j][l] = "O"
        elif game[i] == "1":
            gamestate[j][l] = "X"
        else:
            gamestate[j][l] = "-"
        
        l += 1
        if l % 7==0:
            j+=1
            l=0
            
    return np.array(np.array(gamestate, dtype=np.str_), dtype=np.str_)


@app.route('/c4b/game/<gamestate>')
def getGamestate(gamestate):
    state = str(gamestate)
    player = 1
    with open('./gamestate.csv', 'a') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow([player, state])

    with open('./pain.csv', 'a') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow([0, 0])
    
    return redirect('/c4b/p')


@app.route('/c4b/p')
def theBoard():
    
    # lastPlayer = int(pd.read_csv('pain.csv')['Player'].iloc[-1])
    # get last index of the column 'Turn'
    while (0 == int(pd.read_csv('pain.csv')['Player'].iloc[-1])):
        # while 0 means the client made the most recent move
        time.sleep(2) # average time to make a move
        # print("sleep")
        continue

    df = pd.read_csv('pain.csv')
    # get the last move that was made
    col = df['Column'].iloc[-1]

    
    # once the column has been "GET"
    # change the player #, so has to wait until the remote player makes a move

    # with open('./gamestate.txt', 'w') as f:
    #     f.write(gamestate)
    #     # using csv.writer method from CSV package
    #     # write = csv.writer(f)
    #     # write.writerow(gamestate)
    data = {"move": str(col)}
    return jsonify(data)
    # return render_template('showMove.html', move = col)

# on pico side after getting the column from 'theBoard' then should go to the url getGamestate passing the gamestate


@app.route("/logout")
def logout():
    logout_user()
    flash('Logged out!', 'success')
    return redirect(url_for('index'))

'''
@app.route("/C4B/start", methods=['POST', 'GET'])
def connectFourStart():
    # Write to element of sql database then remove element in the connect 4 code
    # Start script so ig
    '''

'''When button pressed redirect to c4b play, have function for first time play--Probably something creative in the db
    Need an import statement for these
    start_state = init_board()
    play_game(start_state)'''
    
'''
    global turn, run, state, nextp

    turn = 0
    run = True
    state = init_board()
    nextp = next_player(state)
    
    return render_template('connect4_start.html')


@app.route("/C4B/play", methods=['GET', 'POST'])
def connectFourPlay():
    # global MOVES_LEFT
    # cb4.print_board(state)
    global turn, run, state, nextp

    

    while run:
        # player = player1 if next_player(state) == 1 else player2

        if (nextp):
            # computer move
            move, state_next = get_move(state)
            # MAX max Max Maxwell maxwell  your code here
            # move is an int with range [0-6] inclusive, corresponding to a column

        else:
            
           
            move = None
            while move not in state:
                try:
                    move = request.form.get('player_column')
                    # instead of input here do the form get?
                    # wait until there is a value in the form get yeah probably the purpose of the submit button
                except ValueError:
                    continue
            
            state = dict(successors(state))
            # max your code here
            # move = wait_for_move() # column number human chose [0-6]
            state_next = update_board_with_move(state, move) # keep line
            

        # MOVES_LEFT -= 1

        print("Turn {}:".format(turn))
        print("Player {} moves to column {}".format(1 if nextp else 2, move))
        print_board(state_next)

        turn += 1
        state = state_next
        if (is_full(state) or has_win(state)):
            run = False
        nextp = 1 - nextp

    score1, score2 = scores(state)
    if score1 > score2:
        print("Player 1 wins!")
    elif score1 < score2:
        print("Player 2 wins!")
    else:
        print("It's a tie.")
    
    # Write to element of sql database then remove element in the connect 4 code
    
    return render_template('connect4.html')

'''
# Check if username or email are already taken
def user_exsists(username, email):
    # Get all Users in SQL
    users = User.query.all()
    for user in users:
        if username == user.username or email == user.email:
            return True

    # No matching user
    return False

    

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')



@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)



@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))
