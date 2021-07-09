import imaplib
import email
import getpass
import re
import os
import sys


SERVER = "imap.gmail.com"
PORT = 993


def get_credentials():

    global USER_EMAIL
    global USER_PASSWORD

    USER_EMAIL = input('Email: ')
    USER_PASSWORD = getpass.getpass()

    return (USER_EMAIL, USER_PASSWORD)


def que_py_file(pno, data, file_name):
    file_name = re.sub('[?*<>|/!%]', '', file_name)

    if f'p{pno}_{file_name}.py' in os.listdir():
        print(f'p{pno}_{file_name}............ALREADY DONE!!')
        return

    with open(f'p{pno}_{file_name}.py', 'w', encoding='utf-8') as file:
        file.write('"""\n{}\n"""'.format(data))
        print(f'p{pno}_{file_name}.............DONE!!')


def que_list_txt(qno, que_name):
    with open('question.txt', 'a+', encoding='utf-8') as file:
        file.seek(0)
        content = file.read().splitlines()
        if f'{qno}. {que_name}' not in content:
            file.seek(2)
            file.write(f'{qno}. {que_name}\n')


def snake_name(title):
    return title.replace(' ', '_').lower()


def generate_data(raw_data):
    # TODO: create to extract right info
    if raw_data.is_multipart():
        for part in raw_data.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
                break
    else:
        body = raw_data.get_payload(decode=True)

    body = body.decode("utf-8").split('---')[0]
    body = body.replace(
        '[The Daily Byte](http://thedailybyte.dev)\r\n\r\nGood morning,\r\n\r\n', '')
    body = body.replace('\r\n\r\nThanks,\r\nThe Daily Byte\r\n\r\n', '')
    body = body.replace('\r\n\r\n', '\n')

    return body


def read_email():
    try:
        mail = imaplib.IMAP4_SSL(host=SERVER, port=PORT)
        mail.login(USER_EMAIL, USER_PASSWORD)
        mail.select(mailbox='INBOX', readonly=False)

        _typ, msg_id = mail.search(None, '(FROM "byte@thedailybyte.dev")')
        ids = msg_id[0].decode("utf-8").split(' ')
        pno = 1

        for num in ids[2:]:
            _typ, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1].decode("utf-8"))

            if sys.argv[1] == 'list':
                que_list_txt(qno=pno,
                             que_name=msg['Subject'])

            else:
                que_py_file(pno=pno,
                            data=generate_data(msg),
                            file_name=snake_name(msg['Subject']))

            pno += 1

    except Exception as e:
        print(e)


def print_help():
    print('''HELP:
(this program only create python files for now)
use following argument:
-----------------------

update : to update the list of questions, or add missing questions.
list: generate a .txt file with the list of question names.
help: to print help.
    ''')


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        if len(sys.argv) == 1 or sys.argv[1].lower() == 'help':
            print_help()

        elif sys.argv[1].lower() == 'update':
            get_credentials()
            print('Updating...........')
            read_email()
            print('[ALL DONE!!]')

        elif sys.argv[1].lower() == 'list':
            get_credentials()
            print('Generating...........')
            read_email()
            print('DONE!! questions.txt generated')

        else:
            print('use valid argument, or no argument')
    else:
        print('use valid argument, or no argument')
