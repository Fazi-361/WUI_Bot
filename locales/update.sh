pybabel extract -k _:1,1t -k _:1,2 -k __ --input-dirs=. -o locales/messages.pot --project=WiiWiiUBot
pybabel update -l US -d locales -D messages -i locales/messages.pot -N --ignore-obsolete --ignore-pot-creation-date --omit-header
sed -i '1s/^/msgid ""\nmsgstr ""\n"X-Crowdin-SourceKey: msgstr\\n"\n\n/' ./locales/US/LC_MESSAGES/messages.po
pybabel update -l IT -d locales -D messages -i locales/messages.pot -N --ignore-obsolete --ignore-pot-creation-date --omit-header
echo "Now update the language files!"