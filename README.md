# GitLab Email Hook
Storing last short sha1 commit in sql. After pushing new commit to remote server if 
new short sha1 commit not equal with short sha1 commit in sql, script sending email 
following format and updating sql.

Also if new repo created, script detect new repo and insert new repo to last_commit sql table

# Email Format



    Commit Repo: githlab-email-repo
    Branch Name: master
    User: gokhan
    User Mail: gokhan@mankara.og
    Commit Message: First Test Email Commit
    Commit Time: 2015-05-30T13:58:42.000+03:00
    
    Diff URL: https://gitlab.domain.com/gokhan/gitlab-email-repo/compare/s1ws93...1ex4ng59
