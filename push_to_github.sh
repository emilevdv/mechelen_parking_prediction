#!/bin/bash

cd ~/Documents/mechelen_parking_prediction
git init
git add .
git commit -m "Force update: complete local version"
git remote remove origin 2> /dev/null
git remote add origin https://github.com/emilevdv/mechelen_parking_prediction.git
git branch -M main
git push -u origin main --force