#!/bin/bash

# Ga naar je projectmap (pas aan als nodig)
cd ~/Documents/mechelen_parking_prediction

# Stage alle wijzigingen (toegevoegd, aangepast, verwijderd)
git add .

# Vraag een korte commit message of gebruik default
read -p "Commit message (of enter voor default): " msg
if [ -z "$msg" ]; then
    msg="Update project"
fi

# Maak commit
git commit -m "$msg"

# Push naar GitHub
git push

echo "Alle wijzigingen zijn veilig geüpload naar GitHub!"