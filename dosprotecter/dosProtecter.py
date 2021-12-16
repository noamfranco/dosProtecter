import time
from dosprotecter.limitLearner import *
from dosprotecter.constants import *
from dosprotecter.rateCounter import *
import smtplib

class DosProtecter:
    def __init__(self,seed_rate,jail_time = JAIL_TIME,dos_trshould = DOS_TRESHOULD,
    time_frame = TIME_FRAME,ddos_treshould = 8) -> None:
        self.limit_learner = limitLearner(seed_rate)
        self.jail_time = jail_time
        self.dos_treshould = dos_trshould
        self.time_frame = time_frame
        self.ddos_treshould = ddos_treshould
        self.email_service = False
        self.builder()
    
    def builder(self):
        self.last_email_time = 0
        self.in_ddos_mode = False
        self.ips_behaviors = {}
        self.in_quarantine = []
        self.jail_times = {}
        self.counter = 0
        self.email_time = 0
    
    def add_email_service(self,send_username,send_pass,mail):
        self.mail = mail
        self.send_username = send_username
        self.send_pass = send_pass
        self.email_service = True

    def add_report(self,ip):
        self.counter += 1
        if ip in self.in_quarantine and self.jail_times[ip] < time.time() - self.jail_time:
            self.in_quarantine.remove(ip)
        
        if not ip in self.ips_behaviors:
            self.ips_behaviors[ip] = rateCounter(self.time_frame)
        
        events = self.ips_behaviors[ip].add_event()
        if events > self.limit_learner.normal_rate * self.dos_treshould:
            self.in_quarantine.append(ip)
            self.jail_times[ip] = time.time()
        
        elif time.time() - self.ips_behaviors[ip].start_time > self.time_frame:
            self.limit_learner.add_report(events,min(0.1,(1 / self.counter)))

        if len(self.in_quarantine) > self.ddos_treshould:
            self.ddos_mode_on()
            if self.email_service and time.time() > self.last_email_time:
                self.send_email()
            
    
    def ddos_mode_on(self):
        if self.in_ddos_mode:
            return 
        print('You Are being ddos attacked!!')
        self.initial_limit = self.limit_learner.normal_rate
        self.limit_learner.normal_rate /= 1.8
        self.in_ddos_mode = True
    
    def ddos_mode_off(self):
        if not self.in_ddos_mode:
            return
        self.limit_learner.normal_rate = self.initial_limit
        self.in_ddos_mode = False


    def send_email(self):
        gmail_user = self.send_username
        gmail_password = self.send_pass

        sent_from = gmail_user
        to = [self.mail]
        subject = "Youre being ddos attacked"
        body = 'Youre being ddos attacked'

        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (sent_from, ", ".join(to), subject, body)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, to, message)
            server.close()

            print('ddos Email sent!')
        except Exception as e:
            print(e)