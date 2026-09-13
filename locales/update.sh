pybabel extract -k _:1,1t -k _:1,2 -k __ --input-dirs=. -o locales/messages.pot --no-location --project=WiiWiiUBot
pybabel update -l US -d locales -D messages -i locales/messages.pot -N --ignore-obsolete --ignore-pot-creation-date
pybabel update -l IT -d locales -D messages -i locales/messages.pot -N --ignore-obsolete --ignore-pot-creation-date
echo "Now update the language files!"