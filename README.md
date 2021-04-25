# Python-Flask-Web-Chat-App
This is a web app for chatting made with the flask framework. I have used a mysql database created in phpmyadmin for this project. This is more of a functionality based project so I have not focussed on the styling (css) part. The styling could definitely be a lot better and if you'd like you can modify it. I used bootstrap which made the front-end very easy and quick. 

The functionalities of this project are as follows:-
..There is a login and register function and pages you want to show in your actual project cannot be accessed without signing in. The logged in user is remembered by the app until the user logs out.
..In the actual app now, there are multiple pages, namely home, all users, search users, chat list and profile. 
-There is nothing much in the homepage except for a welcome message for the user that logged in
-In the all users page, as the name suggests, all the users that have an account for this web app (except for the current user) are listed with their information such as their first name, last name, email and username. There is also a button for each user in this page. When clicked on, the button takes the user to a page where the current user can chat with the user they chose.
-In the search users page, the user can search for a user on the basis of their first name, last name and username. If the user searched for themselves they won't get anything in return.
-In the chat list page, the user can view all the messages with all the people they have texted in this app.
-In the profile page, the user can view all their information, i.e, their first name, last name, email and username. It is not editable. On this page, there's also an option to set a profile picture for themselves which will be saved in the database and also the static folder of this project.
..Now about the chat page where the user actually can send messages to someone
-simple text messages can be sent
-if the current user sends a message, the options displayed under that message will be: Delete | Edit | Forward | Reply
-and if someone else sends the current user a message, the options displayed under that message will be: Forward | Reply since we don't want the current user to be able to delete and edit someone else's messages other than their own
-if the delete button is pressed, the message will be deleted
-if the edit button is pressed, the user will be able to edit their message
-if the forward button is pressed, the user will be able to forward the message to anyone who has an account in this app; the user will be shown a list of all users except themselves and will be able to forward the selected user that message
-if the reply button is pressed, the user will be able to reply to either their own message or someone else's message

..In this chat page, if the user has set their profile picture, then it will be displayed with each message they send and if the person they're talking to has set their profile picture, then it will be displayed with every message that person sends.

Those are all the functionalities of this project. If I add some more, I will commit them to here and hopefully you like this project.
