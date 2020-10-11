# Project 1

Web Programming with Python and JavaScript

Book store web application using flask framewrok
link of a video of the application:
https://www.youtube.com/watch?v=26xwcf9BmFY

In my import.py file:

I have a function the reads the info from the csv file I have and Insert them into my database table books

In my application.py file:

I have 8 functions I will explain them in detail:-

first function (index): it returns the indx.html page which is my homepage

second function (login): If the mesthod is post it takes information from the form I made in the login.html page and check if the username and password recieved are correct and if the password matches the username it set the session name to the username and turn the session logged in into True, but if the information are incorrect it returns the login page again with error message
And if the method is get it just returns the login page

Third function(sign up): It takes the information from my sign up form made in the signup.html and check if there is no users with the same username, and if there is no users with the same username it insert a new user information to the tabke users in my database and if there is any user with the same username it returns an error

Fourth function (Logout): it pops out the username from the session and changes the logged in into False and redirect to the home page

Fifth Function (dashboard): If the method is get it just returns a search form but you can't use this search unless you are logged in, so if the method is post it checks if you are logged in or no, if youu are not logged in it returns an error and if you are logged in in search in the database about something like what was written in the form if it found it returns it, but if it didn't find it will just return error message


Sixth function (book):this function takes from goodread api rate count and rate average and generate a dunamic url with the isbn of the book, and return special information about each book and let you add your review and comment just once.

seventh function (error): returns an error message

last function (book api): uses the isbn of the book to generate a json text with all info about that book

in templates folder I have all the html files, and static folder all the css and imgs I am using


