# Main application flow
from flask import Flask, request, redirect
from models import Base, User, Job
from flask_sqlalchemy import SQLAlchemy
import twilio.twiml
import re
import datetime
from list import list
from sendMessage import sendMessage

app =  Flask(__name__
app.config['SQLALCHEMY_DATABASE_URI'] = ''
db = SQLAlchemy(app)

# Handle all texts 
@app.route("/", methods=['GET', 'POST'])
def reply():

    # Each time a request is made, first check for and
    # update depricated pending jobs (TEST THIS)
    db.session.query(Job).filter(Job.deadline < datetime.datetime.now(), Job.status == 0).update({"status": 2})
    db.session.commit()

    # The content of the message
    text = request.values.get('Body', None)

    # The phone number sending the message
    from_number = request.values.get('From', None)

    # Regular expressions for various matches
    # Note, they only match at the beginning of the text
    regMatch = re.compile('^Register', re.IGNORECASE)
    startMatch = re.compile('^Start', re.IGNORECASE)
    helpMatch = re.compile('^List', re.IGNORECASE)
    jobMatch = re.compile('^Job', re.IGNORECASE)
    acceptMatch = re.compile('^Accept', re.IGNORECASE)
    completeMatch = re.compile('^Complete', re.IGNORECASE)
    requestMatch = re.compile('^Request', re.IGNORECASE)
    dutiesMatch = re.compile('^Duties', re.IGNORECASE)

    # Registration
    if regMatch.match(str(text)):
        response = register(text, from_number)

    # Start
    elif startMatch.match(str(text)):
        return

    # Job
    elif jobMatch.match(str(text)):
        response = job(text, from_number)

    # List
    elif helpMatch.match(str(text)):
        response = list()

    # Accept
    elif acceptMatch.match(str(text)):
        response = accept(text, from_number)

    # Complete
    elif completeMatch.match(str(text)):
        response = complete(text, from_number)

    # Request
    elif requestMatch.match(str(text)):
        response = requestJobs(from_number)

    # Duties
    elif dutiesMatch.match(str(text)):
        response = duties(from_number)

    # All other text
    else:
        response = "Unrecognized command. Pleae text 'LIST' for a complete " \
        "list of valid operations."
 
    resp = twilio.twiml.Response()
    resp.sms(response)

    return str(resp)


# Handle registration texts (must enter first and last name)
def register(text, from_number):
    split = text.split()
    if len(split) < 3:
        return "Please enter a first and last name. Text 'LIST' for a complete "\
                "explanation of all commands."
    else:
        fullName = " ".join([split[1], split[2]]).title()

        ## Name not working!
        if db.session.query(User).filter_by(number=from_number).count():
            db.session.query(User).filter_by(number=from_number).update({"name": fullName.title()})
            db.session.commit()
            return "You have already registered this number. Your name has been changed to %s." % fullName.title()

        else:
            user = User(name=fullName, number=from_number)
            db.session.add(user)
            db.session.commit()
            return "Thanks for registering, %s." % fullName.title()


# Handle the 'request' command (to request a list of jobs with IDs)
def requestJobs(from_number):
    
    # In case the user has not registered
    name = db.session.query(User).filter_by(number=from_number).scalar()
    if name is None:
        return "Woh there! You must register before requesting a list of jobs. Text 'LIST' for a complete " \
                "explanation of all commands."

    # Issued jobs
    jobs = db.session.query(Job).filter_by(status=0)

    if jobs.count() == 0:
        return "No pending jobs. Please check back later!"

    jobList, singleJob = "", ""
    for job in jobs:
        singleJob = "(ID: %d) - %s from %s to %s by %s" % (job.id, job.what, job.fromTown,
        job.toTown, str(job.deadline.strftime("%d-%m-%Y")))
        jobList = "\n\n".join([jobList, singleJob])

    return jobList


# Handle the 'job' command to make  new job
def job(text, from_number):

    # In case the user has not registered
    name = db.session.query(User).filter_by(number=from_number).scalar()
    if name is None:
        return "Woh there! You must register before submitting a job. Text 'LIST' for a complete " \
                "explanation of all commands."
    else:
        name = name.name

    lower = text.lower()
    split = lower.split()

    # Not all keywords specified exception
    if not all(x in split for x in ['from', 'to', 'in']):
        return "You must specify values for each input parameter. Text 'LIST' for a complete "\
                "explanation of all commands."

    # Parse the message
    ind = 0
    days = 365
    fromTown, toTown, what = '', '', ''
    for word in split:
        
        if word == 'from':
            ind = 1
            continue
        if word == 'to':
            ind = 2
            continue
        if word == 'in':
            ind = 3
            continue


        if ind == 0:
            if word == 'job':
                continue
            else:
                what += word + " "

        if ind == 1:
            fromTown += word + " "
        elif ind == 2:
            toTown += word + " "
        elif ind == 3:
            try:
                days = int(word)
            except ValueError:
                return "Please enter a valid integer for the number of days. Text 'LIST' for a complete " \
                "explanation of all commands."
            else:
                ind = 4

    deadline = datetime.datetime.now() + datetime.timedelta(days=days)
    job = Job(what = what.capitalize().rstrip(), owner = from_number, deadline = deadline, \
        fromTown = fromTown.title().rstrip(), toTown = toTown.title().rstrip())
    
    db.session.add(job)
    db.session.commit()

    return "Thanks, %s! Your job has been issued. The job ID is %d." % (name, job.id)


# Handle the 'accept' command (with a job ID)
def accept(text, from_number):

    # In case the user has not registered
    name = db.session.query(User).filter_by(number=from_number).scalar()
    if name is None:
        return "Woh there! You must register before accepting a job. Text 'LIST' for a complete " \
                "explanation of all commands."
    else:
        name = name.name

    split = text.split()

    try:
        idVal = int(split[1])
    except (ValueError, IndexError) as e:
        return "Please enter a valid ID number. Text 'LIST' for a complete " \
        "explanation of all commands."

    job = db.session.query(Job).filter_by(id=idVal).scalar()
    jobUpdate = db.session.query(Job).filter_by(id=idVal)

    # Job ID doesn't exist
    if job is None:
        return "Please enter a valid ID number. Text 'LIST' for a complete " \
        "explanation of all commands."

    # Has already been claimed or has explired
    elif job.status > 0:
        return "This job has either expired, or has been claimed."
    
    # An acceptable job
    else:
        owner = job.owner
        ownerName = db.session.query(User).filter_by(number=owner).scalar()
        ownerName = ownerName.name

        jobUpdate.update({"accepter": from_number})
        jobUpdate.update({"status": 1})
        db.session.commit()

        # Send a message to the job owner
        textBody = "Hi there, %s. %s has accepted your job (job ID %d). Text %s at %s"\
            " to organize further details." %(ownerName, name, idVal, name, from_number) 
        sendMessage(owner, textBody)

        return "Thanks, %s! You have accepted this job. Text %s at %s"\
            " to organize further details." % (name, ownerName, owner)


# Handle the 'complete' command (with a job ID)
def complete(text, from_number):

    # In case the user has not registered
    name = db.session.query(User).filter_by(number=from_number).scalar()
    if name is None:
        return "Woh there! You must register before completing a job. Text 'LIST' for a complete " \
                "explanation of all commands."
    else:
        name = name.name

    split = text.split()

    try:
		idVal = int(split[1])
    except (ValueError, IndexError) as e:
		return "Please enter a valid ID number. Text 'LIST' for a complete " \
        "explanation of all commands."

    job = db.session.query(Job).filter_by(id=idVal).scalar()
    jobUpdate = db.session.query(Job).filter_by(id=idVal)

    # Job ID doesn't exist
    if job is None:
        return "Please enter a valid ID number. Text 'LIST' for a complete " \
        "explanation of all commands."

    # Has already been completed or has not been accepted or
    elif job.status == 0 or job.status == 3:
        return "This job has either never been accepted, or has already been completed."

    # If this is not the correct owner
    elif job.accepter != from_number:
        return "You did not accept this job. You therefore cannot complete it."

    
    # An acceptable job
    else:
        owner = job.owner
        ownerName = db.session.query(User).filter_by(number=owner).scalar()
        ownerName = ownerName.name

        jobUpdate.update({"status": 3})
        jobUpdate.update({"endDate": datetime.datetime.now()})
        db.session.commit()

        # Send a message to the job owner
        textBody = "Hi there, %s. %s has completed your job (job ID %d)." %(ownerName, name, idVal) 
        sendMessage(owner, textBody)

        return "Thanks, %s! You have completed this job." % name


# Handle the 'Duties' command
def duties(from_number):

    # In case the user has not registered
    name = db.session.query(User).filter_by(number=from_number).scalar()
    if name is None:
        return "Woh there! You must register before participating in this service. Text 'LIST' "\
                "for a complete explanation of all commands."
    else:
        name = name.name

    jobs = db.session.query(Job).filter(Job.accepter == from_number, Job.status == 1)

    # This user has no accepted jobs
    if jobs.count() == 0:
        return "You currently have no accepted jobs."

    jobList, singleJob = "", ""
    for job in jobs:
        singleJob = "(ID: %d) - %s from %s to %s by %s. Owner: %s." % (job.id, job.what, job.fromTown,
        job.toTown, str(job.deadline.strftime("%d-%m-%Y")), job.owner)
        jobList = "\n\n".join([jobList, singleJob])

    return jobList


# Delete completed or expired jobs
def deleteJobs():
    db.session.query(Job).filter(Job.status > 1).delete()
    db.session.commit()

# Setup data base (clearing anything in a previous instance)
def setup():
    # Recreate database each launch
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)

# Print the contents of both datbases
def check():
    print "USERS"
    users = db.session.query(User).all()
    for user in users:
        print user

    print " "
    print "JOBS"

    jobs = db.session.query(Job).all()
    for job in jobs:
        print job

if __name__ == "__main__":
    app.run(debug=True)