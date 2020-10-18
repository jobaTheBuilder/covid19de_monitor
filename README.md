# covid19de_monitor

A simple python script to retrieve COVID19 data from the german RKI (Robert Koch-Institut).

## Motivation

The script is used collect 7-day-by-100K-people incidents for a pre-defined number of cities.
The interesting cities are defined in the script by name of the city and the city attribute.

The data API of the RKI is used:
https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0

## Example

The statement

```
target_areas = [{'GEN': 'Würzburg', 'BEZ': 'Kreisfreie Stadt'},              
                {'GEN': 'Fürstenfeldbruck', 'BEZ': 'Landkreis'}]
```

defines the cities Würzburg and Fürstenfeldbruck as intereysting cities to 
collect incident data for.


## Compatibilty

The script is used with Python 3.8