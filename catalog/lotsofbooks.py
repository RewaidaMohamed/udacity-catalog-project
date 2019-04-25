from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from librarydb_setup import Library, Base, Book, User, Genre

engine = create_engine('sqlite:///library.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Start of Book Genres Table
# Add Genre 1
genre1 = Genre(name="Drama")
session.add(genre1)
session.commit()
# Add Genre 2
genre2 = Genre(name="Comedy")
session.add(genre2)
session.commit()
# Add Genre 3
genre3 = Genre(name="Fantasy")
session.add(genre3)
session.commit()
# Add Genre 4
genre4 = Genre(name="Historical")
session.add(genre4)
session.commit()
# Add Genre 5
genre5 = Genre(name="Horror")
session.add(genre5)
session.commit()
# Add Genre 6
genre6 = Genre(name="Romance")
session.add(genre6)
session.commit()
# Add Genre 7
genre7 = Genre(name="Mystery")
session.add(genre7)
session.commit()
# Add Genre 8
genre8 = Genre(name="Action and Adventure")
session.add(genre8)
session.commit()
# Add Genre 9
genre9 = Genre(name="Crime and Detective")
session.add(genre9)
session.commit()
# Add Genre 10
genre10 = Genre(name="Science Fiction")
session.add(genre10)
session.commit()
# End of Book Genres Table


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com")
session.add(User1)
session.commit()


# Menu for UrbanBurger
library1 = Library(user_id=1, name="Alex Book Center")

session.add(library1)
session.commit()

book1 = Book(user_id=1,
             title="Everything I Never Told You",
             author="Celeste Ng",
             description="Thats going to be a really sad story "
             "about someone dying",
             genre=genre6,
             library=library1)

session.add(book1)
session.commit()

book2 = Book(user_id=1,
             title="Is Everyone Hanging Out Without Me?",
             author="Mindy Kaling",
             description="Lorem ipsum dolor sit amet, consectetur "
             "adipiscing elit, sed do eiusmod tempor incididunt ut "
             "labore et dolore magna aliqua",
             genre=genre1,
             library=library1)

session.add(book2)
session.commit()

print "Books Added!"
