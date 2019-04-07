#!/usr/bin/env python
import os
import biplist
import smtplib
import argparse
import sys
import traceback
import time


def main():
    exported = 0

    try:
        parser = argparse.ArgumentParser(
            description='Export Safari Reading List to Pocket!')
        parser.add_argument('email', metavar='email', type=str,
                            help='User e-mail connected to Pocket')
        parser.add_argument('password', metavar='password', type=str,
                            help='User password')
        parser.add_argument('smtp', metavar='smtp', type=str,
                            help='SMTP server to use')
        parser.add_argument('--count', metavar='N', type=int,
                            default=-1, help='How many entries to export')
        parser.add_argument('--smtp-port', metavar='smtp-port', type=int,
                            default=587, help='SMTP port to use')
        parser.add_argument('--timeout', metavar='timeout', type=int,
                            default=1, help='Custom timeout between requests')
        args = vars(parser.parse_args())

        from_addr = args['email']
        password = args['password']
        to_addr = 'add@getpocket.com'
        count = args['count']
        smtp_server = args['smtp']
        smtp_port = args['smtp_port']
        timeout = args['timeout']

        # load bookmarks plist into a dictionary
        fullpath = os.path.join(os.environ['HOME'],
                                'Library/Safari/Bookmarks.plist')
        plist = biplist.readPlist(fullpath)

        # find the "Reading List" node
        for child in plist['Children']:
            if child.get('Title', None) == 'com.apple.ReadingList':
                rl = child['Children']

                # prepare an SMTP server connection
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.ehlo()
                server.starttls()
                server.login(from_addr, password)

                # start sending URLs to Pocket, which in turn will
                # auto-magically add them to your reading list.
                for entry in rl:
                    url = entry['URLString']

                    print 'Sending: ' + url

                    msg = "\r\n".join([
                        "From: " + from_addr,
                        "To: " + to_addr,
                        "Subject: " + url,
                        "",
                        url
                    ])
                    server.sendmail(from_addr, to_addr, msg)
                    exported = exported + 1

                    # Export up to "count" if specified
                    if count != -1 and exported >= count:
                        break

                    time.sleep(timeout)

    except KeyboardInterrupt:
        print "\nCtrl+C received, shutting down...\nExported: " + str(exported)
        sys.exit(0)
    except Exception:
        traceback.print_exc(file=sys.stdout)

    print 'Done. Exported ' + str(exported) + '!'
    sys.exit(0)


if __name__ == "__main__":
    main()
