# Mastermind

## Prerequisites
- Since this app is containerized, Docker is the only dependency you need to run it:
https://www.docker.com/products/docker-desktop/

## Installation
1. Fork and clone the repository to your local machine.
2. In your terminal, navigate to the root project folder mastermind:
   ```
   cd mastermind2024
   ```
3. Before building the containers, you first need to set up the environment variables (for accessing your MySQL database as well as setting the secret key for auth tokens).
- ### **Create a .env file in the root folder with the following template:**

    ```
    # Database configuration
    MYSQL_ROOT_PASSWORD=rootpassword
    MYSQL_DATABASE=mastermind
    MYSQL_USER=mastermind_user
    MYSQL_PASSWORD=userpassword

    # Django secret key
    SECRET_KEY=your_secret_key
    ```
- ### **You can copy/paste the default values that are provided here, but for app security I recommend you input your own unique values.**

4. **Make sure you have Docker running before proceeding.**
5. Build and start the container with the following command in the terminal:
   ```
   docker-compose up --build
   ```
6. While Docker builds and establishes ports it may attempt connecting to the DB several times, this is normal. Once you see that it has finished "Applying" migrations and "OK", it is ready to go.
7. Open a web browser and go to: 

```
http://localhost:3000/login
```

## Usage

### Login/Register
- On the landing page, you are prompted to log in or register. Click on the register button and enter a new username and password. Once successful, it will automatically take you to the game screen. You will be able to login with those same credentials moving forward.

### Gameplay
- The goal of this game is to guess a secret number within 10 tries. Before the game starts, you can use the "Difficulty" selector to change the amount of numbers you need to guess if you'd like. It is set to "4" by default. Otherwise, you can click on New Game to start. 
- The game controls will now be activated, and the timer will start. Click on the number-buttons to input a guess, and the submit-button to send it in. You will receive feedback on your attempt based on: the numbers correct, and the numbers in the correct position. Use this feedback to make a decision for your next attempt. If all of the numbers are in the correct position, you will "Win" which will: increase your win counter by 1, stop the timer, and add a new "time" to your record. If you lose, the timer simply stops and waits until you start a New Game. Try to beat your fastest time!

### Leaderboard Stats
- Your total wins and fastest time are stored in memory, but they only count for the difficulty you have selected. This means if you switch to a new difficulty, it will have its own unique total win count and fastest time. 

### Logging Out/Exiting Game
- If you log out, the game will pause the timer so that you can continue where you left off once you log back in. It will also pause the timer if you close the window and then return to the game page. 


## Design
### My Thoughts
This is my second attempt at building a Mastermind game for the LinkedIn REACH program, and the improvements between this version and the previous version are **staggering** to me. Not only is the backend built in a new language/framework, but it's a massive improvement on the scalability of the overall design, the organization, the readability, even when considering the added layer of complexity of the authentication system. I'm so proud of what I've been able to accomplish since the last cycle! 

### Framework and Language
This application is built on a hybrid system of a Django backend - and a React frontend. Everything is packaged together with the help of Docker containers. With the built-in features that Django offers, I was able to create a backend server with a:
- Secure game-user system, in combination with MySQL's database user system
- Robust set of data models with rigorous data validation
- Powerful ORM combined with a serializer layer to validate data and keep it organized 
- Thoroughly tested REST APIs/Views with Django's Rest Framework

Django's framework allowed me to keep my code clean and readable. Since I chose to give the game a UI, I was able to combine the Django backend server with React. I've found this hybrid system to be very successful, and allowed for a clear separation of concerns when testing and debugging. 

### Data Model

The application follows these 4 models:

**PlayerProfile** - Represents a new user, their difficulty setting, and their current Game ID

**Game** - Holds the secret number for each Game, the Player it belongs to, and Game info

**Round** - Each Round contains the Player's guess, and feedback about how accurate it was

**Leaderboard** - An aggregate of the Player's wins/losses, and their Game times

### API/Views
The API supplies data to the frontend in the following flow:

**Initializing Game state:**
A GET request is sent for the following data:
- Player's username, difficulty setting, and current game ID*
- *If current Game exists, the Round data of that Game (history of Player's guess attempts)
- The start-time of the Game (to calculate the timer state)
- Leaderboard data: total wins and their fastest win time

**Starting a new Game:**
A POST request is sent:
- To the backend with the Player's difficulty setting. The backend polls an external API using the Player's difficulty number
- The Player's "current game" ID is updated with the new Game ID
- The Game ID is used to fetch the updated Round data, and the start-time

**Making a guess:**
A POST request is sent:
- With the Player's guess, the backend compares it with the secret number and updates the database with new round data*
- *If the player guesses correctly, the leaderboard is updated with a win and a completion time

**Updating Difficulty:**
A PATCH request is sent:
- With the Player's new difficulty setting, and updates it

**Resuming the Timer:**
A PATCH request is made:
- With the Player's pause time, the backend calculates the duration of time missed and updates the Game's original start time to offset and correct the timer

## Extensions
- **Hints**: Adding support to offer hints about the secret number when the player clicks the "hint" button. 
- **Updated Timer**: Currently, the timer stores information when you log out and then updates your timer when you log back in. I would like to reconfigure it so it updates the timer without even having to log back in. 

# Thank you for checking out Mastermind!
I had a lot of fun being able to express the amount of growth I've had since the last cycle!

Feel free to message me about it, please connect with me on LinkedIn:
https://www.linkedin.com/in/ortega-david-e/


---