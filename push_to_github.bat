git remote add origin https://github.com/0khacha/smart-document-converter.git > git_push.log 2>&1
git branch -M main >> git_push.log 2>&1
git push -u origin main >> git_push.log 2>&1
