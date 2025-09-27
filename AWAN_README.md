# AWAN AI Flask Quiz App



Table of contents
1. [Installation](#installation)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)
6. [Contact](#contact)


## Installation

```bash
# clone this repo
$ git clone https://github.com/Lin-Jet/awan-quiz-flask.git

# go to the directory
$ cd awan-quiz-flask

# use updated virtual env
$ virtualenv ENV_UPDATED && source ENV_UPDATED/bin/activate

# install dependencies
$ pip install -r updated_requirements.txt

# export flask app and run
$ set FLASK_APP=main.py
$ flask run

```

## Usage

app.db has been preloaded with

6000 stratified random sampled questions for Full TechTCM Evaluation Set
374 multiple answer items and 5626 single answer items.  There can be 4 to 5 answer choices

Capable of handling 120 users.

We would ideally need 100 users.

First 3 users will answer first 150 questions.
Second 3 users will answer second 150 questions.
...
Last 3 users will answer last 150 questions. 


Users will answer the multichoice question, select category, and select difficulty.
They may flag the question if they feel the question has any errors.

There is an individual question timer and a overall question timer that is calculated by adding up individual times.  Users may pause their time


Keyboard shortcuts are provided for faster quiz taking.

upon completion a exact match score and total time will be displayed.


## License
Distributed under the MIT License. See LICENSE for more information.

## Original Author

Name: Boobalan Shettiyar - boopalanshettiyar78@gmail.com
ProjectLink: https://github.com/thepasterover/flask-quiz-app


