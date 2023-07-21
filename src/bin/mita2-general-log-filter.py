#!/usr/bin/python3

import re
import sys
import getopt

class GeneralLogFilter:

    USAGE = 'USAGE: mita2-general-log-filter [--user user] [--command command] [--no-mask] [--help] < general-log-file'

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "command=", "no-mask", "help"])
            opts = dict(opts)
        except getopt.GetoptError as err:
            print(self.USAGE)
            sys.exit(1)

        if '--help' in opts.keys():
            print(self.USAGE)
            sys.exit(0)

        session_user = {}
        query = ''
        time = ''
        session_cmd = ''
        cmd = ''

        for line in sys.stdin.readlines():
            line = line.strip()

            if (re.match(r'/usr/sbin/mysqld', line)):
                continue
            elif (re.match(r'Tcp port: [0-9]+', line)):
                continue
            elif (re.match(r'Time\s+Id', line)):
                continue
            elif (re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+(\+[0-9]{2}:[0-9]{2}|Z)', line)):
                if query != "":
                    output = True

                    if '--user' in opts.keys() and not session_user[session_id] == opts['--user']:
                        output = False

                    if '--command' in opts.keys() and cmd != opts['--command']:
                        output = False

                    if not '--no-mask' in opts.keys():
                        query = re.sub(r"'[^']+'", "'S'", query)
                        query = re.sub(r'"[^"]+"', "'S'", query)
                        query = re.sub(r'\b\d+\b', 'N', query)

                    if output:
                        print("%s\t%s\t%s" % (time, session_cmd, query))

                query = ''
                cmd = ''
                session_cmd = ''

                parts = line.split("\t")
                if len(parts) == 2:
                    time = parts[0]
                    session_cmd = parts[1]
                    query = ''
                elif len(parts) == 3:
                    time, session_cmd, query = parts
                else:
                    raise Exception('Unkown format %s' % line)

                match = re.match(r' *([0-9]+) (\w+)', session_cmd)
                session_id = match.group(1)
                cmd = match.group(2)

                if cmd == 'Connect' and not re.match(r'Access denied for user', query):
                    match = re.match(r'([^@]+)@[^@]+ on .+', query)
                    user = match.group(1)
                    session_user[session_id] = user

            else:
                query = query + ' ' + line


if __name__ == '__main__':
    log_filter = GeneralLogFilter()
    log_filter.main()
