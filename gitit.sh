git add .

echo "Please enter commit comment"

read commit

git commit -m $commit

git push origin master
