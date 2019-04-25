#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookStores.

This modules contains the functions that handles Library app.
"""
from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify, flash, make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from librarydb_setup import Base, Library, Book, Genre, User

import httplib2
import json
import requests
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Library List App"

app = Flask(__name__)

engine = create_engine('sqlite:///library.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/libraries/JSON')
def librariesJSON():
    """Return List of Libraries in JSON format."""
    libraries = session.query(Library).all()
    return jsonify(libraries=[i.serialize for i in libraries])


@app.route('/libraries/<int:library_id>/books/JSON')
def showBooksJSON(library_id):
    """Return List of Books owned by a specific Library in JSON."""
    library = session.query(Library).filter_by(id=library_id).one()
    books = session.query(Book).filter_by(library_id=library.id).all()
    return jsonify(books=[i.serialize for i in books])


@app.route('/libraries/<int:library_id>/books/<int:book_id>/JSON')
def showOneBookJSON(library_id, book_id):
    """Return information of a Book in JSON."""
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=book.serialize)


@app.route('/JSON')
def showLatestBooksJSON():
    """Return the Latest Books in JSON format."""
    latest = session.query(Book).limit(10).all()
    return jsonify(books=[i.serialize for i in latest])


@app.route('/genre/<int:genre_id>/books/JSON')
def showBooksByGenre(genre_id):
    """Return List of Book for specific Genre in JSON."""
    books = session.query(Book).filter_by(genre_id=genre_id).all()
    return jsonify(books=[i.serialize for i in books])


@app.route('/')
def showHomePage():
    """
    HomePage Handler.

    Show Home Page for users containing different genres.
    And the latest books added.
    """
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
    else:
        user_id = 0
    genres = session.query(Genre).all()
    books = session.query(Book).limit(10).all()
    return render_template('index.html', current_user_id=user_id,
                           genres=genres, books=books, title="Latest Books")


@app.route('/genre/<int:genre_id>/books')
def showGenreBooks(genre_id):
    """Return List of Books by genre_id."""
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
    else:
        user_id = 0
    genres = session.query(Genre).all()
    books = session.query(Book).filter_by(genre_id=genre_id).all()
    selected_genre = session.query(Genre).filter_by(id=genre_id).one()
    return render_template('index.html', current_user_id=user_id,
                           genres=genres, books=books,
                           title=selected_genre.name)


@app.route('/libraries')
def showLibraries():
    """Return Library List."""
    libraries = session.query(Library).all()
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
    else:
        user_id = 0
    return render_template('libraries.html', libraries=libraries,
                           current_user_id=user_id)


@app.route('/libraries/new', methods=['GET', 'POST'])
def addNewLibrary():
    """Add New Library."""
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newlibrary = Library(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newlibrary)
        session.commit()
        flash('New library Added!')
        return redirect(url_for('showLibraries'))
    else:
        return render_template('newLibrary.html')


@app.route('/libraries/<int:library_id>/edit', methods=['GET', 'POST'])
def editLibrary(library_id):
    """Edit Library Information."""
    if 'username' not in login_session:
        return redirect('/login')
    editedLibrary = session.query(Library).filter_by(id=library_id).one()
    if editedLibrary.user_id != login_session['user_id']:
        return """<script>
        function myFunction() {
            alert('You are not authorized to edit this Library.');
        }
        </script>
        <body onload='myFunction()''>"""
    if request.method == 'POST':
        if request.form['name']:
            editedLibrary.name = request.form['name']
        session.add(editedLibrary)
        session.commit()
        flash('Library Successfully Edited!')
        return redirect(url_for('showLibraries'))
    else:
        return render_template('editLibrary.html', library=editedLibrary)


@app.route('/libraries/<int:library_id>/delete', methods=['GET', 'POST'])
def deleteLibrary(library_id):
    """Delete Library."""
    if 'username' not in login_session:
        return redirect('/login')
    selectedLibrary = session.query(Library).filter_by(id=library_id).one()
    if selectedLibrary.user_id != login_session['user_id']:
        return """<script>
            function myFunction() {
                alert('You are not authorized to delete this Library.');
            }
            </script>
            <body onload='myFunction()''>"""
    if request.method == 'POST':
        session.delete(selectedLibrary)
        booksToDelete = session.query(Book).filter_by(
                        library_id=selectedLibrary.id).all()
        for book in booksToDelete:
            session.delete(book)
        session.commit()
        flash('Library Successfully Deleted!')
        return redirect(url_for('showLibraries'))
    else:
        return render_template('deleteLibrary.html', library=selectedLibrary)


@app.route('/libraries/<int:library_id>')
@app.route('/libraries/<int:library_id>/books')
def showLibraryBooks(library_id):
    """Return Books List for specific library."""
    library = session.query(Library).filter_by(id=library_id).one()
    books = session.query(Book).filter_by(library_id=library.id)
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
    else:
        user_id = 0
    return render_template('books.html', library=library,
                           books=books, current_user_id=user_id)


@app.route('/libraries/<int:library_id>/books/new', methods=['GET', 'POST'])
def addNewBook(library_id):
    """Add new book to a library."""
    if 'username' not in login_session:
        return redirect('/login')
    library = session.query(Library).filter_by(id=library_id).one()
    if library.user_id != login_session['user_id']:
        return """<script>
            function myFunction() {
                alert('You are not authorized to add books to this Library.');
            }
            </script>
            <body onload='myFunction()''>"""
    genres = session.query(Genre).all()
    if request.method == 'POST':
        newBook = Book(title=request.form['title'],
                       author=request.form['author'],
                       description=request.form['description'],
                       genre_id=request.form['genre'],
                       library_id=library.id,
                       user_id=login_session['user_id'])
        session.add(newBook)
        session.commit()
        flash('New book Added!')
        return redirect(url_for('showLibraryBooks', library_id=library.id))
    else:
        return render_template('newBook.html', library=library, genres=genres)


@app.route('/libraries/<int:library_id>/books/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(library_id, book_id):
    """Edit Book."""
    if 'username' not in login_session:
        return redirect('/login')
    library = session.query(Library).filter_by(id=library_id).one()
    editedBook = session.query(Book).filter_by(id=book_id).one()
    if editedBook.user_id != login_session['user_id']:
        return """<script>
            function myFunction() {
                alert('You are not authorized to Edit this book.');
            }
            </script>
            <body onload='myFunction()''>"""
    genres = session.query(Genre).all()
    if request.method == 'POST':
        if request.form['title']:
            editedBook.name = request.form['title']
        editedBook.author = request.form['author']
        editedBook.genre_id = request.form['genre']
        editedBook.description = request.form['description']
        session.add(editedBook)
        session.commit()
        flash('Book Successfully Edited!')
        return redirect(url_for('showLibraryBooks', library_id=library.id))
    else:
        return render_template('editBook.html', library=library,
                               book=editedBook,
                               genres=genres)


@app.route('/libraries/<int:library_id>/books/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(library_id, book_id):
    """Delete Book."""
    if 'username' not in login_session:
        return redirect('/login')
    selectedLibrary = session.query(Library).filter_by(id=library_id).one()
    selectedBook = session.query(Book).filter_by(id=book_id).one()
    if selectedBook.user_id != login_session['user_id']:
        return """<script>
            function myFunction() {
                alert('You are not authorized to Edit this book.');
            }</script>
            <body onload='myFunction()''>"""
    if request.method == 'POST':
        session.delete(selectedBook)
        session.commit()
        flash('Book Successfully Deleted!')
        return redirect(url_for('showLibraryBooks',
                        library_id=selectedLibrary.id))
    else:
        return render_template('deleteBook.html', library=selectedLibrary,
                               book=selectedBook)


@app.route('/login')
def showLogin():
    """
    Login Page.

    prepare unique string for each login session.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google Login."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'),
                                200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 300px; height: 300px;
              border-radius: 150px;
              -webkit-border-radius: 150px;
              -moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Google disconnect."""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """FaceBook Login."""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'
    'grant_type=fb_exchange_token&'
    'client_id=%s&client_secret=%s'
    '&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in
        the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?'
    'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?'
    'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; '
    'height: 300px;border-radius: 150px;'
    '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """FaceBook Disconnect."""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    """
    User Disconnect.

    Disconnect based on provider.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showHomePage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showHomePage'))


def createUser(login_session):
    """Create a New User."""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Return user object by user id."""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Return user ID."""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
