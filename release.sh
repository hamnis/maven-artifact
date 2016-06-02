#!/bin/bash

asksure() {
echo -n "Are you sure (Y/N)? "
while read -r -n 1 -s answer; do
  if [[ $answer = [YyNn] ]]; then
    [[ $answer = [Yy] ]] && retval=0
    [[ $answer = [Nn] ]] && retval=1
    break
  fi
done

echo # just a final linefeed, optics...

return $retval
}

if [ "Z$1" = "Z"  ]; then
echo "Not a valid version number"
exit 1
fi

echo Releasing $1
if asksure; then

./build.sh

cat > version <<EOF
$1
EOF

git add version
git commit -m "Setting to release $1"
echo "Tagging $1"
git tag v$1

cd dist
gpg --sign -a maven_artifact-$1-py2.py3-none-any.whl
cd ..
twine upload dist/maven_artifact-$1-py2.py3-none-any.whl
else
  echo "Not releasing $1"
fi
