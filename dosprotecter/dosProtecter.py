import time
from dosprotecter.limitLearner import *
from dosprotecter.constants import *
from dosprotecter.rateCounter import *
import smtplib
import pycountry
#import matplotlib.pyplot as plt
from urllib.request import urlopen
from json import load


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

        self.quarentine_lst = []
    
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
        
    def plot_quarntine(self):
        print(self.quarentine_lst)
        plt.plot(list(self.quarentine_lst))
        plt.show()

    def add_report(self, ip):
        self.counter += 1
        
        if ip in self.in_quarantine:
            if self.jail_times[ip] < time.time() - self.jail_time:
                self.in_quarantine.remove(ip)
                self.hasher.update_ip_hashes(self.in_quarantine)
                self.ips_behaviors[ip] = rateCounter(self.time_frame)
            self.quarentine_lst.append(len(self.in_quarantine))
            return

        if not ip in self.ips_behaviors:
            self.ips_behaviors[ip] = rateCounter(self.time_frame)
        
        events = self.ips_behaviors[ip].add_event()
        if events > self.limit_learner.normal_rate * self.dos_treshould:
            self.in_quarantine.append(ip)
            self.jail_times[ip] = time.time()
        
        elif time.time() - self.ips_behaviors[ip].start_time > self.time_frame:
            self.limit_learner.add_report(events,min(0.1,(1 / self.counter)))

        if len(self.in_quarantine) > self.ddos_treshould and not self.in_ddos_mode:
            self.ddos_mode_on()
            if self.email_service and time.time() > self.last_email_time:
                self.send_email()
        
        self.quarentine_lst.append(len(self.in_quarantine))

        return ip in self.in_quarantine
            
    def ddos_mode_on(self):
        if not self.in_ddos_mode:
            print('You Are being ddos attacked!!')
            self.initial_limit = self.limit_learner.normal_rate
            self.limit_learner.normal_rate /= 1.8
            self.in_ddos_mode = True
    
    def ddos_mode_off(self):
        if self.in_ddos_mode:
            self.limit_learner.normal_rate = self.initial_limit
            self.in_ddos_mode = False
    
    def get_ips_regions(self):
        regions = [self.get_ip_region(ip) for ip in self.in_quarantine]
        print(regions)
        return regions
    
    def get_ip_region(self, addr=''):
        if addr == '':
            url = 'https://ipinfo.io/json'
        else:
            url = 'https://ipinfo.io/' + addr + '/json'
        try:
            res = urlopen(url)
            #response from url(if res==None then check connection)
            data = load(res)
            #will load the json response into data
            if 'country' in data:
                return pycountry.countries.get(alpha_2=data['country']).name
            else:
                return 'Unknown'
        except:
            return 'Unknown'

    def send_email(self):
        gmail_user = self.send_username
        gmail_password = self.send_pass

        sent_from = gmail_user
        to = [self.mail]
        subject = "Youre being ddos attacked"
        body = f'Youre being ddos attacked the suspicious ips regions are: {self.get_ips_regions()}'

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
