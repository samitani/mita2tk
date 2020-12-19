#!/usr/bin/python3

import sys
import re
import getopt
import random
import time
import datetime
import string

class BinlogMask:
    USAGE = '''\
USAGE: mysqlbinlog -vv --base64-output=DECODE-ROWS binlog-file | mita2-general-log-filter.py [--preserve=schema.table.column_pos,schema.table.column_pos...]

This script masks values in your decoded binary log.
Binlog must be ROW formatted. Check your binlog_format is ROW.\
'''

    def rand_str(self, length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def shift_date(self, date, seconds_shift):
        fmt =  '%Y-%m-%d %H:%M:%S'
        shifted = datetime.datetime.strptime(date, fmt) + datetime.timedelta(seconds=seconds_shift)

        return shifted.strftime(fmt)

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["help", "preserve="])
            opts = dict(opts)
        except getopt.GetoptError as err:
            print(self.USAGE)
            sys.exit(1)

        if '--help' in opts.keys():
            print(self.USAGE)
            sys.exit(0)

        preserve = []
        if '--preserve' in opts.keys():
            preserve = opts['--preserve'].split(',')

        # max 2 week
        timeshift = random.randint(0, 60 * 60 * 24 * 14)

        for line in sys.stdin.readlines():
            ### UPDATE `test`.`t`
            ### WHERE
            ###   @1=3 /* LONGINT meta=0 nullable=0 is_null=0 */
            ###   @2='THIS IS SECRET STRING2' /* VARSTRING(255) meta=255 nullable=0 is_null=0 */
            ###   @3=2000 /* INT meta=0 nullable=1 is_null=0 */
            ###   @4='2020-12-13 06:28:54' /* DATETIME(0) meta=0 nullable=1 is_null=0 */
            ### SET
            ###   @1=3 /* LONGINT meta=0 nullable=0 is_null=0 */
            ###   @2='THIS IS SECRET STRING3' /* VARSTRING(255) meta=255 nullable=0 is_null=0 */
            ###   @3=2000 /* INT meta=0 nullable=1 is_null=0 */
            ###   @4='2020-12-13 06:28:54' /* DATETIME(0) meta=0 nullable=1 is_null=0 */
            valmatch = re.match(r'^(### +@([0-9]+)=)(.+?)( /\*.+)', line)
            objmatch = re.match(r'^### (INSERT INTO|UPDATE) `([^`]+?)`\.`([^`]+?)`', line)

            if objmatch is not None:
                schema  = objmatch.group(2)
                table   = objmatch.group(3)

            if valmatch is not None:
                column  = valmatch.group(1)
                colpos  = valmatch.group(2)
                value   = valmatch.group(3)
                comment = valmatch.group(4)
                
                if schema + "." + table + "." + colpos in preserve:
                    print(line, end='')
                    continue

                if re.match(r' /\* VARSTRING\([0-9]+\) .+', comment):
                    masked = "'" + self.rand_str(len(value) - 2) + "'"
                    print(column + masked + comment)
                elif re.match(r' /\* LONGINT .+', comment):
                    masked = random.randint(0, 2**63 - 1) # SIGNED BIGINT
                    print(column + str(masked) + comment)
                elif re.match(r' /\* INT .+', comment):
                    masked = random.randint(0, 2**32 - 1) # SIGNED INT
                    print(column + str(masked) + comment)
                elif re.match(r' /\* DATETIME\([0-9]+\) .+', comment):
                    masked = "'" + self.shift_date(value.replace("'", ""), timeshift) + "'"
                    print(column + masked + comment)
                elif re.match(r' /\* BLOB/TEXT ', comment):
                    masked = "'" + self.rand_str(len(value) - 2) + "'"
                    print(column + masked + comment)
                else:
                    raise Exception('Unknown TYPE ' + line)
            else:
                print(line, end='')


if __name__ == '__main__':
    binlogmask = BinlogMask()
    binlogmask.main()
