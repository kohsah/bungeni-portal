# encoding: utf-8
# sent time based notifications

# The system should also store the following parameters:
#     * maximum number of days that can elapse between the time a question is sent to the relevant 
#       Ministry and the time the question is placed on the Order Paper.
#     * maximum number of days that may elapse between the days a Minister receives a question 
#       and the day a written response is submitted to the clerk.
#     * maximum number of days that may elapse between the day a question by private notice 
#       (questions that in the opinion of the Speaker are of an urgent nature) is scheduled for reply.

# Notifications will be sent to the Speaker and the Clerk listing all questions that have exceeded the limits stated above. 
import sys
import datetime

import zope.lifecycleevent
from zope.i18n import translate

from email.mime.text import MIMEText


import sqlalchemy.sql.expression as sql

from ore.alchemist import Session
import bungeni.core.workflow.dbutils as dbutils
import bungeni.core.domain as domain
import bungeni.core.schema as schema
import bungeni.core.globalsettings as prefs
#from bungeni.core.workflows.question import states as q_state
from bungeni.server.smtp import dispatch

##############################
# imports for main
from zope import component
from sqlalchemy import create_engine
from ore.alchemist.interfaces import IDatabaseEngine
#import bungeni.core.interfaces
from bungeni import core as model

def _getQuestionsPendingResponse(date, ministry):
    """
    returns all questions that are in the state 
    'pending written response from a ministry'
    and were sent to the ministry before this date
    """
    status = u"Question pending response" #q_state.response_pending
    session = Session()
    qfilter=sql.and_(
                (domain.Question.c.ministry_submit_date < date ),
                (domain.Question.c.status == status),
                (domain.Question.c.ministry_id == ministry.ministry_id)
                )
    query = session.query(domain.Question).filter(qfilter)
    return query.all()



def _getAllMinistries(date):
    """
    returns all ministries that are 
    valid for this date
    """
    session = Session()
    mfilter=sql.or_( 
        sql.between(date, schema.groups.c.start_date, schema.groups.c.end_date),
        sql.and_(
                (schema.groups.c.start_date < date ),
                (schema.groups.c.end_date == None)
                )
        )
    query = session.query(domain.Ministry).filter(mfilter)
    return query.all()
    
def _getMemberOfParliamentEmail(question):
    user_id = question.owner_id
    session = Session()
    user = domain.Person.get(user_id)
    return user.email
    

    
def sendNotificationToMP(date):
    """
    send a mail to the MP asking the question that the deadline 
    of the question is aproaching
    """
    status = u"Question pending response" #q_state.response_pending
    text = translate('notification_email_to_mp_question_pending_response',
                     target_language='en',
                     domain='bungeni.core',
                     default="Questions pending responses.")
    session = Session()
    qfilter=sql.and_(
                (domain.Question.c.ministry_submit_date < date ),
                (domain.Question.c.status == status),
                )
    questions = session.query(domain.Question).filter(qfilter).all()
    for question in questions:
        mailto = _getMemberOfParliamentEmail(question)
        if mailto and question.receive_notification:
            msg = MIMEText(text)
            msg['Subject'] = u'Questions pending response'
            msg['From'] = prefs.getAdministratorsEmail()
            msg['To'] =  mailto
            text = text + '\n' + question.subject + '\n'
            print msg
            #dispatch(msg)
    
def sendNotificationToClerksOffice(date):
    """
    send a mail to the clerks office with
    stating all questions per ministry that
    are approaching the deadline
    """
    text = translate('notification_email_to_clerk_question_pending_response',
                     target_language='en',
                     domain='bungeni.core',
                     default="Questions pending responses.")
    ministries = _getAllMinistries(date)
    for ministry in ministries:
        questions = _getQuestionsPendingResponse(date, ministry)
        if questions:
            text = text + '\n' + ministry.full_name +': \n'
        for question in questions:
            text = text + question.subject + '\n'
    
    msg = MIMEText(text)
    
    msg['Subject'] = u'Questions pending response'
    msg['From'] = prefs.getAdministratorsEmail()
    msg['To'] = prefs.getClerksOfficeEmail()
    print msg
    #dispatch(msg)


def sendNotificationToMinistry(date):
    """
    send a notification to the ministry stating
    all questions that are approaching the deadline
    """
    text = translate('notification_email_to_ministry_question_pending_response',
                     target_language='en',
                     domain='bungeni.core',
                     default="Questions pending responses.")
    ministries = _getAllMinistries(date)
    for ministry in ministries:
        questions = _getQuestionsPendingResponse(date, ministry)
        text = translate('notification_email_to_ministry_question_pending_response',
                     target_language='en',
                     domain='bungeni.core',
                     default="Questions assigned to the ministry pending responses.")
        if questions: 
            text = text + '\n' + ministry.full_name +': \n'
            for question in questions:
                 text = text + question.subject + '\n'
            emails = dbutils.getMinsiteryEmails(ministry)
            msg = MIMEText(text)
            
            msg['Subject'] = u'Questions pending response'
            msg['From'] = prefs.getClerksOfficeEmail()
            msg['To'] = emails
            print msg
            #dispatch(msg)
        
def sendAllNotifications():
    """
    get the timeframes and send all notifications out
    """
    delta = prefs.getDaysToNotifyMinistriesQuestionsPendingResponse()
    date = datetime.date.today()
    sendNotificationToMinistry(date)
    sendNotificationToClerksOffice(date)
    sendNotificationToMP(date)
            
def main(argv=None):
    """
    run this as a cron job and execute all
    time based transitions
    """
    db = create_engine('postgres://localhost/bungeni', echo=False)
    component.provideUtility( db, IDatabaseEngine, 'bungeni-db' )
    model.metadata.bind = db
    session = Session()
     
    sendAllNotifications()
        
    #session.flush()
    #session.commit()
    
if __name__ == "__main__":
    sys.exit(main())

