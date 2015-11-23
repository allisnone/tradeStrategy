"""

Define the functions for sending SMS and Email when alarm/alert is activated/recovered

"""

import smtplib
from email.mime.text import MIMEText
import MySQLdb

"""

"""

""" Main function for sending Email """
#eventlist=[code,cost,current_price,eventtype,date_time,eventinfo]
def sendMail(eventlist):
    code = eventlist[0]
    code='Measurement '+code[2:]
    cost = eventlist[1]
    current_price = eventlist[2]
    eventtype = eventlist[3]
    date_time = eventlist[4]
    #code = eventlist[5]
    eventinfo = eventlist[5]
    inscrease=eventlist[6]
    message = mailContent(date_time, code, eventinfo,inscrease)
    subject = subjectContentMail(code, cost, current_price, eventtype, eventinfo)
    msg = MIMEText(message)       
    msg['Subject'] = subject
    smtp = smtplib.SMTP()
    smtp.connect('142.133.1.1') 
    smtp.sendmail('Administrator@ems.eld.gz.cn.ao.ericsson.se', mailTo(), msg.as_string())  
    smtp.quit() 

""" Main function for sending SMS """    
def sendSMS(eventlist):
    code = eventlist[0] 
    cost = eventlist[1]
    current_price = eventlist[2]
    eventtype = eventlist[3]
    date_time = eventlist[4]
    eventinfo = eventlist[5]
    message = SMSContent(date_time, code, eventinfo,current_price)
    subject = subjectContentSMS(code, cost, current_price, eventtype, eventinfo)
    msg = MIMEText(message)       
    msg['Subject'] = subject
    smtp = smtplib.SMTP()
    smtp.connect('142.133.1.1') 
    smtp.sendmail('Administrator@ems.eld.gz.cn.ao.ericsson.se', SMSTo(), msg.as_string())  
    smtp.quit()

""" Define subject for SMS  """  
def subjectContentSMS(code, cost, current_price, eventtype, eventinfo):
    if eventinfo == 'activate':
        return '[For test ' + code + ' ' + cost + ' ' + current_price + ' ' + eventtype + ' active ] '
    else:
        return '[For test ' + code + ' ' + cost + ' ' + current_price + ' ' + eventtype + ' recovered ] '

""" Define subject for somemail """
def subjectContentMail(code, cost, current_price, eventtype, eventinfo):
    if eventinfo == 'activate':
        return '[For test]'+ ' ' +code+' ' + eventtype + ' ' +eventinfo #'consider to sell when increase some little'
    else:
        return '[For test]' + ' ' +code+' ' + eventtype + ' ' +eventinfo

""" Define Email body """   
def mailContent(date_time, code, eventinfo,current_inscress):
    msg1 = 'Dear User, \n \n'
    if eventinfo == 'activate': 
        message = '  '+ date_time + ' ' + code + ' ' + 'is decreased %s%% now! May lower than you cost! Please take action and consider to sell it!' %current_inscress
    else:
        message1 = '  '+ date_time + ' ' + code + ' ' + "is increased %s%% now.  Higher than you expect!"%current_inscress
        message=message1+ 'You can wait more increase, or satisfy the current profit'
    return msg1+message
    
""" Define SMS body """   
def SMSContent(date_time, code, eventinfo,current_inscress):  
    if eventinfo == 'activate': 
        message = '  '+ date_time + ' ' + code + ' ' + 'is lower than you cost! Please take action and consider to sell it!' 
    else:
        message = '  '+ date_time + ' ' + code + ' ' + 'is higher than the press point!' + 'You can wait more increase, or satisfy the current profit'
    return message

""" Get the mail list from db """
def mailTo(): 
    """
    host = '10.178.250.32'
    port = 3306
    user = 'ems'
    passwd = '1234'
    db = 'emsdb'
    conn = MySQLdb.connect(host, user, passwd, db, port)
    cur = conn.cursor()
    cur.execute('select somemail from v_subscription where alarm_subscription="yes"')
    datalist = cur.fetchall()
    """
    emaillist = ['jason.g.zhang@ericsson.com','david.w.song@ericsson.com']
    """
    for row in datalist:
        emaillist.append(row[0])
    """
    return emaillist 

""" Get the SMS list from db """
def SMSTo():
    """
    host = '10.178.250.32'
    port = 3306
    user = 'ems'
    passwd = '1234'
    db = 'emsdb'
    conn = MySQLdb.connect(host, user, passwd, db, port)
    cur = conn.cursor()
    cur.execute('select phone from v_subscription where alert_subscription="yes"')
    datalist = cur.fetchall()
    smslist = []
    for row in datalist:
        smslist.append(row[0]+'@sms.ericsson.com')
    """
    smslist=['13922119451']
    return smslist


def send_mail(mailto_list,sub,content):
    mailto_list=['104450966@qq.com'] 
    mail_host='smtp.163.com'
    mail_user='zgx20022002@163.com'
    mail_pass='821853Zgx'  
    mail_postfix="qq.com"
    
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    """
    print 'Setting MIMEText'
    CT=open('content.txt','r')  #read the txt
    content=CT.read().decode('utf-8')
    msg=MIMEText(content.encode('utf8'),_subtype='html')
    CT.close()#close tst
    """
    msg = MIMEText(content)  
    msg['Subject'] = sub  
    msg['From'] = mail_user 
    msg['To'] = ";".join(mailto_list)
    try:  
        #s = smtplib.SMTP()
        s=smtplib.SMTP_SSL(mail_host,465)
        s.login(mail_user,mail_pass)  
        s.sendmail(mail_user, mailto_list, msg.as_string())  
        s.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False

mailto_list=['104450966@qq.com']   
if __name__ == '__main__':  
    if send_mail(mailto_list,"here is subject","here is content"):  
        print "send successfully"  
    else:  
        print "send fail" 

#http://lovesoo.org/qq-members-separate-python-script-that-automatically-send-email.html
    