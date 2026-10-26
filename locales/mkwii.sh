pybabel extract -k mk__ --no-default-keywords -o locales/mkwii.pot --no-location --project=WiiWiiUBot bot/handlers/mkwiirandom.py
pybabel update -d locales -D mkwii -i locales/mkwii.pot
pybabel compile -d locales -D mkwii -f