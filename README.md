# cits3001-project
Resistance game
# Author: Aaron Wee and Alex Mai
2 agents is added to play the game

## CITS3403 - ASLUWA - 
##### Diana (22732266), Aaron (22702446), Valerie (22645271), David (22236059)
<br/>

### 1. The purpose of the web application, explaining both the context and the assessment mechanism used.
<br/>

- The purpose of the ASL Web is to educate users on how to communicate in sign language and in particular American Sign Language (known as ASL). It is the primary language of the deaf and hard of hearing in the USA, and its popularity expands to other countries around the world.  

- ASL plays an important role in making communication within the deaf community possible. Sign language is not only the language of the hands. It is a visual language formed by organized hand gestures, body movements, and facial expressions.  

- The ASL Web will teach users 2 main topics, namely, Fingerspelling of the Alphabets, and Basics, which covers greetings and common signs. User will go through a learning page, then a practice section, followed by a test for each of the two topics. The assessment would consists of user-interactive multiple choice style questions.  
<br>
<br>

### 2. Architecture of The Web Application
<br/>

#### MVC 
<br/>


<img src="MVC.png" width="500">

- When the user wants to sign in, they first click on the log in button which then directs them to login.html.
  
- In this example, the view(user) sends a request to the controller as a GET method in routes.py, who processes the request and returns a POST method to the view. 
- The username and password are data stored in the model which the controller manipulates to validate the request.
<br/>
- Model (data)
    - models.py
<br/>
- View (UI)
    - User View
    - forms.py
<br/>
- Controller (uses the view and raises a HTTP request/ request handler)
    - routes.py (GET and POST method)
<br/>
<br/>

### Database Schema
<br/>
CREATE TABLE alembic_version (  <br/>
	version_num VARCHAR(32) NOT NULL, <br/>
	CONSTRAINT alembic_version_pkc PRIMARY KEY <br/>(version_num)<br/>
);  
<br/>

CREATE TABLE roles (<br/>
	id INTEGER NOT NULL, <br/>
	name VARCHAR(50), <br/>
	PRIMARY KEY (id), <br/>
	UNIQUE (name)<br/>
);
<br/>

CREATE TABLE user (<br/>
	id INTEGER NOT NULL, <br/>
	username VARCHAR(64), <br/>
	email VARCHAR(120), <br/>
	password VARCHAR(128), <br/>
	avatar VARCHAR(128), <br/>
	PRIMARY KEY (id)<br/>
);<br/>

CREATE UNIQUE INDEX ix_user_email ON user (email);<br/>
CREATE UNIQUE INDEX ix_user_username ON user (username);<br/>
CREATE TABLE assessment (<br/>
	id INTEGER NOT NULL, <br/> 
	user_id INTEGER, <br/>
	submission TEXT, <br/>
	PRIMARY KEY (id), <br/>
	FOREIGN KEY(user_id) REFERENCES user (id)<br/>
);
<br/>

CREATE TABLE quiz_result  
	id INTEGER NOT NULL,  
	mark INTEGER,  
	total_marks INTEGER,  
	user_id INTEGER,  
	date_time DATETIME,  
	course_num INTEGER,  
	PRIMARY KEY (id),  
	FOREIGN KEY(user_id) REFERENCES user (id)  
);
<br/>

CREATE TABLE user_roles (  
	id INTEGER NOT NULL,  
	user_id INTEGER,  
	role_id INTEGER,  
	PRIMARY KEY (id),  
	FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE,  
	FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE  
);  
<br/>

CREATE TABLE progression (  
	id INTEGER NOT NULL,  
	"current_Learn" INTEGER,  
	current_quiz INTEGER,  
	current_practice INTEGER,  
	course_avg INTEGER,  
	test1_avg INTEGER,  
	test2_avg INTEGER,  
	test1_attempt INTEGER,  
	test2_attempt INTEGER,  
	user_id INTEGER NOT NULL,  
	last_accessed DATETIME,  
	PRIMARY KEY (id),  
	FOREIGN KEY(user_id) REFERENCES user (id),  
	UNIQUE (user_id)  
);

### 3. How To Lauch The Application


1. Go into the directory "cits3403Web".

2. Use source venv/bin/activate to go into the virtual environment. <br/>

3. To install all the necessary packages, enter the following command into the terminal

   *pip install -r requirements.txt*<br/>

4. Go into the cits3403Web folder using *cd cits3403Web* in the terminal<br/>

5. Set up initial admin by the command highlighted int the "Set up inital admin" section below. **(Note that this done only if using fresh db)**

6. In the terminal, use the command *flask run* <br/>

7. Enter http://127.0.0.1:5000/ in any web browser to launch and run the application. <br/>

<br/>

### Set Up Initial Admin
<br/>
Use the below for the initial setup of the Admin user and role:<br/>
<br/>

flask shell<br/>
from app import db<br/>
from app.models import User, Role, UserRoles, Progression<br/>
<br/>

u = User(username='Admin', email='Admin@example.com')<br/>

db.session.add(u)<br/>
db.session.commit()<br/>
<br/>

u = User.query.get(1)<br/>
u.set_password('1234')<br/>
<br/>

admin_role = Role(name='Admin')<br/>
db.session.commit()<br/>
u = User.query.get(1)<br/>
u.roles = [admin_role,]<br/>
db.session.commit()<br/>

user.progress = Progression(user_id = u.id)<br/>
db.session.commit()<br/>
<br/>


### Admin Login

- Click "Login". <br/>
- Enter username: Admin<br/>
- Enter password: 1234<br/>

- Here you are able to access the general view of the statistics. 
<br/>
<br/>

### 4. Describe some unit tests for the web application, and how to run them.

Run the command pyton test.py

<br/>


#### Test User Creation
- This creates 10 users directly and checks if they exist in the db 
- Expects 10 users in db
<br/>
<br/>

#### Test Login
- This tries to login as a non-user - expects fail
- Registers a user using /resister
- Logs in & out as the registered user - expects success
<br/>
<br/>

#### Test Duplicate Registration
- This tries registering two identical users via /register - expects failure
<br/>
<br/>

#### Test Basics Submission

- This sends a post with score data to the basics webpage - expects success
<br/>
<br/>

#### Test Alphabets Submission

- This sends a post with score data to the alphabets webpage - expects success
<br/>
<br/>

#### Test Quiz Insert

- This inserts quiz results directly and tests it works - expects success
<br/>
<br/>

#### Test Progress Insert
- This inserts does a test update of progress and checks it worked - expects success
<br/>
<br/>

#### Test Permissions
- Creates a non admin user and tries to access an admin only page - expects fail.
- Then creates an admin and check it can access an admin only page - expects success
<br/>
<br/>

#### Test avatar
- Changes user avatar and checks it is stored correctly - expects success
  
<br/>
<br/>

#### Test User Edit
- tests changing a users username - expects success
<br/>
- These have been written as unit tests in test.py <br/>
- To run these ensure you are in the venv environment and run: python test.py
<br/>
<br/>
### 5. Include commit logs, showing contributions and review from all contributing students.

- Refer to git-log.txt
<br/>
<br/>

### References

- Basics Word Image Reference:  -https://takelessons.com/blog/asl-for-beginners-
<br/>

- Alphabets Image Reference:  -https://www.teachersprintables.net/category/sign_language-
<br/>

- Alphabets GIFs Reference:  -https://cudoo.com/blog/most-popular-sign-language-phrases-you-need-to-know/-
<br/>

- Animate On Scroll Library: -https://michalsnik.github.io/aos/-

- Bar Chart: -https://www.chartjs.org/docs/latest/charts/bar.html-

- Bootstrap: -https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css-

- JavaScript: -https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js-

- Flask Avatars: -https://pypi.org/project/Flask-Avatars/#data-

- Flask Login: -https://pypi.org/project/Flask-Login/#data-

- Flask Migrate: -https://pypi.org/project/Flask-Migrate/#data- 

- Flask Mail: -https://pypi.org/project/Flask-Mail/#data-

- Flask Moment: -https://pypi.org/project/Flask-Moment/#data-

- Flask SQL: -https://pypi.org/project/Flask-SQAlchemy/#data-

- Flask Unit Test: -https://pypi.org/project/flask-unittest/#data-

- Flask User: -https://pypi.org/project/Flask-User/#data-

- Flask WTF: -https://pypi.org/project/Flask-WTF/#data-

- Flask Werkzeug: -https://pypi.org/project/Werkzeug/#data-

- Flask WTForms: -https://pypi.org/project/WTForms/#data-
