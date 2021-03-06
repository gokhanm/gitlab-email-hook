#!/usr/bin/env python
__author__ = "Gokhan MANKARA <gokhan@mankara.org"

import gitlab
import sqlite3 as sql
import requests
import smtplib
import os
import email.utils
from email.mime.text import MIMEText

gitlab_url = "https://gitlab.domain.com"
gitlab_access_token = "ABCDEFG"


class SendEmail(object):
    def __init__(self):
        self.mail_to = 'to@domain.com'
        self.mail_from = 'from@domain.com'
        self.mail_server = 'mail.domain.com'
        self.mail_subject = 'New Commit'

    def main(self, msg):
        msg = MIMEText(msg)
        msg['To'] = email.utils.formataddr(('Recipient', self.mail_to))
        msg['From'] = email.utils.formataddr((self.mail_subject, self.mail_from))
        msg['Subject'] = self.mail_subject

        server = smtplib.SMTP(self.mail_server, 25)
        server.set_debuglevel(False)

        try:
            server.sendmail(self.mail_from, self.mail_to, msg.as_string())
        finally:
            server.quit()


class Commit(object):
    def __init__(self):
        self.db = "commits.db"
        self.con = sql.connect(self.db)
        self.git = gitlab.Gitlab(gitlab_url, token=gitlab_access_token, verify_ssl=False)
        with self.con:
            self.cur = self.con.cursor()
        requests.packages.urllib3.disable_warnings()

        if not os.path.isfile(self.db):
            os.system("sqlite3 commits.db < commits.sql")

    def sql_insert(self, repo, branch, hash, group_name):
        sql = "insert into last_commit ('repo', 'branch', 'hash', 'group_name') values ('%s', '%s', '%s', '%s')" %\
              (repo, branch, hash, group_name)

        self.cur.execute(sql)
        self.con.commit()

    def sql_select(self, branch, repo, group_name):
        sql = "select hash from `last_commit` where branch='%s' and repo='%s' and group_name='%s'" %\
              (branch, repo, group_name)

        self.cur.execute(sql)
        return self.cur.fetchone()[0]

    def sql_update(self, new_hash, branch, repo, group_name):
        sql = "UPDATE last_commit SET hash='%s' WHERE branch='%s' and repo='%s' and group_name='%s'" %\
              (new_hash, branch, repo, group_name)

        self.cur.execute(sql)
        self.con.commit()

    def commits(self):
        global author_email
        global author_message
        global author_name
        global commit_date

        # git.getprojectsall => Returns a dictionary of all the projects for admins only
        # git.getprojects => Returns a dictionary of all the projects

        for i in self.git.getprojectsall():
            group_name = i["namespace"]["name"]
            project_name = i["path"]
            project_id = i["id"]
            for branches in self.git.getbranches(project_id):
                    new_commit = branches["commit"]["id"][:8]
                    branch_name = branches["name"]

                    try:
                        commit_in_sql = self.sql_select(branch_name, project_name, group_name)
                    except TypeError:
                        self.sql_insert(project_name, branch_name, new_commit, group_name)

                    if commit_in_sql != new_commit:
                        get_commit_info = self.git.getrepositorycommit(project_id, new_commit)
                        try:
                            author_name = get_commit_info["author_name"]
                            author_email = get_commit_info["author_email"]
                            author_message = get_commit_info["title"]
                            commit_date = get_commit_info["created_at"]
                        except TypeError:
                            pass

                        compare_url = "%s/%s/%s/compare/%s...%s" %\
                                      (gitlab_url, group_name, project_name, commit_in_sql, new_commit)
                        send_email = SendEmail()
                        msg = 'Commit Repo: %s\nBranch Name: %s\nUser: %s\nUser Mail: %s\nCommit Message: %sCommit Time: %s\n\nDiff URL: %s' %\
                              (project_name, branch_name, author_name, author_email, author_message, commit_date, compare_url)
                        send_email.main(msg)
                        self.sql_update(new_commit, branch_name, project_name, group_name)

    def main(self):
        self.commits()


if __name__ == "__main__":
    Commit().main()