pybabel extract -k _:1,1t -k _:1,2 -k __ --input-dirs=. -o locales/messages.pot --no-location --project=WiiWiiUBot
pybabel update -d locales -D messages -i locales/messages.pot
echo "Now update the language files!"