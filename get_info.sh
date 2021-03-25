#!/usr/bin/env bash

inz=$(python3 COVIDUpdate.py -i Würzburg)
beds=$(./IntensivregisterUpdate.py -s Würzburg)
impf=$(./ImpfungUpdate.py -bl BY -a )
impf1=$(./ImpfungUpdate.py -bl BY -vf)
impf2=$(./ImpfungUpdate.py -bl BY -vs)

echo "${inz}"
echo "Belegte Intensivbetten in Würzburg: ${beds}"
echo "Durchgeführte Impfugnen in Bayern ${impf} (Erstimpfung: ${impf1} / Zweitimpfung: ${impf2})"
