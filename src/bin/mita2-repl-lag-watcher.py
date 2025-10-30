#!/usr/bin/python3

import re
import sys
import getopt
import time
import getpass
import datetime
import multiprocessing as mp
import os
import signal
import pymysql

TABLE_NAME = "mita2_repl_lag_watcher"
UPDATE_INTERVAL = 1

class ReplLagWatcher:

    USAGE = 'USAGE: mita2-repl-lag-watcher [--source-host host] [--source-port port] [--replica-host host] [--replica-port port] [--database database] [--user user] [--password password] [--help]'

    def _get_db_connection(self, host, port, user, password, database):
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        return conn

    def _continuous_replica_checker(self):
        replica_conn = self._get_db_connection(self.opts['--replica-host'], int(self.opts['--replica-port']), self.opts['--user'], self.opts['--password'], self.opts['--database'])

        try:
            previous_updated = None
            select_query = f"SELECT updated FROM {TABLE_NAME} WHERE id = 1"

            with replica_conn.cursor() as cursor:
                while True:
                    cursor.execute(select_query)
                    result = cursor.fetchone()

                    if result:
                        current_updated = result['updated']

                        # レプリカのタイムスタンプが前回読み取った時刻よりも新しければ、更新が到達したと判断
                        if current_updated != previous_updated:
                            if previous_updated is not None:
                                local_time = datetime.datetime.now()
                                time_difference = local_time - current_updated

                                # datetime.timedelta をMS単位の float に変換
                                lag = (time_difference.total_seconds() * 1000)

                                print(f"Last Update: {current_updated.strftime('%Y-%m-%d %H:%M:%S.%f')}, Local Time: {local_time.strftime('%Y-%m-%d %H:%M:%S.%f')}, Replication Lag: **{lag:.3f} ms**")

                            previous_updated = current_updated
        except Exception as err:
            print(f"Fatal error reading from replica: {err}")
        finally:
            replica_conn.close()

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["source-host=", "source-port=", "replica-host=", "replica-port=", "database=", "user=", "password=", "help"])
            self.opts = dict(opts)
        except getopt.GetoptError as err:
            print(self.USAGE)
            sys.exit(1)

        if '--help' in self.opts.keys():
            print(self.USAGE)
            sys.exit(0)

        if '--source-host' not in self.opts.keys() \
           or '--replica-host' not in self.opts.keys():
            print(self.USAGE)
            sys.exit(0)

        if '--source-port' not in self.opts.keys():
            self.opts['--source-port'] = 3306

        if '--replica-port' not in self.opts.keys():
            self.opts['--replica-port'] = 3306

        if '--user' not in self.opts.keys():
            self.opts['--user'] = getpass.getuser()

        if '--password' not in self.opts.keys():
            self.opts['--password'] = ''

        if '--database' not in self.opts.keys():
            self.opts['--database'] = 'test'

        try:
            source_conn  = self._get_db_connection(self.opts['--source-host'], int(self.opts['--source-port']), self.opts['--user'], self.opts['--password'], self.opts['--database'])
        except Exception as e:
            print(e)
            sys.exit(1)

        # initialize
        try:
            with source_conn.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id INT PRIMARY KEY,
                    updated DATETIME(6)
                )
                """
                cursor.execute(create_table_query)
            
                insert_initial_query = f"""INSERT INTO {TABLE_NAME} (id, updated) VALUES (1, NOW(6)) ON DUPLICATE KEY UPDATE updated = NOW(6)"""
                cursor.execute(insert_initial_query)
        except Exception as e:
            print(e)
            sys.exit(1)

        # wait for creating the table
        time.sleep(1)

        # launch monitor process
        replica_watcher = mp.Process(
            target=self._continuous_replica_checker,
        )
        replica_watcher.start()

        print("-" * 50)
        print(f"Starting continuous lag check (UPDATE interval: {UPDATE_INTERVAL}s)")
        print("Press Ctrl-C to stop.")
        print("-" * 50)

        # update record
        try:
            with source_conn.cursor() as cursor:
                while True:
                    update_query = f"UPDATE {TABLE_NAME} SET updated = NOW(6) WHERE id = 1"
                    cursor.execute(update_query)

                    if not replica_watcher.is_alive():
                        break

                    time.sleep(UPDATE_INTERVAL)
        except KeyboardInterrupt:
            replica_watcher.terminate()
        except Exception as e:
            print(e)
            sys.exit(1)

        replica_watcher.join()

if __name__ == '__main__':
    watcher = ReplLagWatcher()
    watcher.main()
