import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP server configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")  # Replace with the appropriate port number
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


english_welcome_message = """
                Hello there!

                Welcome to Sema App Platform.

                We are thrilled to take you through more about this platform.
                Sema Platform is a civic technology open platform built to empower democratic participation
                through polling, Ideation, Collaboration, and access to digital services platform aimed to
                strengthen civic participation among citizens and government interactions in building stronger
                and inclusive digital democracies.
                
                The Sema App layout is divided into three parts;
                a. Poll:
                    - On this part, the User may involve the community of other users in deciding on a
                    matter by votes. This may be used in gathering opinions or agreeing on a certain
                    matter. The segment is also open for use by community leaders and their people
                    within the local government jurisdiction, where a matter involves a group of
                    smaller populations.
                    - User Manual: Go to Polls
                b. Forum:
                    - This section of the App is a place for community gatherings, where one may
                    conduct meetings, debates, or forum-related activities, found in this app, in
                    accordance to the terms and conditions of the use
                    - User manual: Go to Forums
                c. Blog:
                    - On a Blog, one may be able to find government materials like policies, and late
                    announcements, publish governance-related materials, and act as an information
                    center to the people.
                    - User Manual: Go to Blogs.

                We once again welcome you to explore more and effectively utilize the forum created
                specifically to Increase Citizens to citizens-to-government civic engagements (C2G). We look
                forward to engaging with you and shaping our evolving democratic institutions at the Sema
                hackathon.
                On any comments or feedback, kindly contact us +255679585176 for more information, queries
                or comments.
            """

swahili_welcome_message = """
                Tupo na furaha kubwa kuwaeleza zaidi kuhusu jukwaa hili.
                
                Jukwaa la Sema ni jukwaa huru la teknolojia ya kiraia lililoundwa kwa lengo la kuwawezesha
                wananchi kushiriki kikamilifu katika mchakato wa kidemokrasia kupitia upigaji kura, kubuni
                mawazo, ushirikiano, na upatikanaji wa huduma za kidigitali. Lengo ni kuimarisha ushiriki wa
                kiraia kati ya wananchi na serikali ili kujenga demokrasia imara na yenye kuingiza watu wote.
                
                Muundo wa Programu ya Sema umegawanywa katika sehemu tatu:
                a. Kura ya maoni:
                    - Katika sehemu hii, Mtumiaji anaweza kushirikisha jamii nyingine ya watumiaji katika kupiga
                    kura kuhusu suala fulani. Hii inaweza kutumiwa kuchangisha maoni au kufikia makubaliano
                    kuhusu jambo fulani. Sehemu hii pia inapatikana kwa matumizi ya viongozi wa jamii na wananchi
                    wao ndani ya mamlaka za serikali za mitaa, inapohusisha kundi la watu wachache.
                    - Mwongozo wa Mtumiaji: Nenda kwenye Kura+
                
                b. Jukwaa:
                    - Sehemu hii ya Programu ni mahali pa mikusanyiko ya jamii, ambapo mtu anaweza kufanya
                    mikutano, mijadala, au shughuli zinazohusiana na jukwaa hili, kulingana na sheria na masharti ya
                    matumizi.
                    - Mwongozo wa Mtumiaji: Nenda kwenye Jukwaa+
                
                c. Blogu:
                    - Kwenye Blogu, mtu anaweza kupata nyaraka za serikali kama sera na tangazo za hivi karibuni,
                    kuchapisha nyaraka za kuhusiana na utawala, na kutumika kama kituo cha habari kwa watu.
                    - Mwongozo wa Mtumiaji: Nenda kwenye Kura+.
                    Tunaendelea kuwakaribisha kutuchunguza zaidi na kutumia jukwaa hili kwa ufanisi, ambalo
                    limewekwa mahsusi kwa kuongeza ushiriki wa raia kwa raia-na-serikali (C2G). Tunatarajia
                    kushirikiana nanyi na kuchora taasisi zetu za kidemokrasia zinazoendelea katika Sema hackathon.
                    
                Kwa maoni au maoni yoyote, tafadhali wasiliana na ………………………………….. kwa maelezo zaidi,
                maswali au maoni.
            """


def send_email(recipient_email, subject, message):
    try:
        # Create a multipart message
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Add message body
        msg.attach(MIMEText(message, "plain"))

        # Create SMTP server connection
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            # server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            # Send email
            server.send_message(msg)

    except Exception as e:
        print("An error occurred while sending the email:", str(e))

    return True
