=====================================================================
			SUMMARY
=====================================================================

This project implements a "Bookstores" interface where you can create your own bookstore and add books with different genres using Python framework Flask along with implementing third-party OAuth authentication.

=====================================================================
			REQUIRMENTS
=====================================================================

to run this project you will need to install the following:
- Vagrant
- VirtualBok
- Python v3
- Flask

to run the code:
- launch the vagrant VM (vagrant up & vargant ssh)
- change directory to /vagrant
- place the project in this directory 
- setup the database by running (python librarydb_setup.py)
- add test data (python lotsofbooks.py) [this step is optional]
- the run the project (python application.py)
- test the application by visiting http://localhost:5000 localy

=====================================================================
			DESCRIPTION
=====================================================================

In this application, you can:
- create your own bookstores
- edit your bookstores
- or delete them
you alse can:
- add books to your bookstore and identify the title, author, description and its Genre
- edit your books information
- or delete them
you can also Sign up to the application using third parties as:
- Google
- Facebook



