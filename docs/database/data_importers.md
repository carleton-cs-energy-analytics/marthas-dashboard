# Data Importers

One of the things that we've been working on this last several weeks is getting data importers ready for live data.  We've only gotten so far as getting in historical data as of rn.  

## What we've done

* UPDATE when we've done point descriptions stuff
* Siemens importers are up and running, for individual file information see the README
* Lucid importers are up and running, ask Jon to add these to README
* Database has a lot of real values
* We made a database! Info in DB Structure wiki.

## Still TODO

* Look at TODO tags in the code, most of them haven't been done, some of them might not need to be any more though
* Talk to Martha, get ALC data, ask about point descriptions JSON not matching csvs
* Get Lucid data into db
* Update point description logic so that we have more information on what each point is, so far on this one we have the branch get_more_points_in which this work has started on
* Finish adding all historical data --> but do this after point description stuff is updated because then we wont have to do it twice and before doing it reset the database jic --> RUN V1 AND V2!!
* Get live data coming at us
* Scripts to add this data into our database
* Documentation on some of the things
* Tests
* Make an unknown room NULL instead of _Dummy_Room_

## How to Run Importers

```bash
nohup python3 -u -m src.datareaders.siemens.siemens_reader <Building Name> <CSV File> &
tail nohup.out
```
Runs it in background so you can leave server and it will still add points, this is good because adding points takes a while for the very large dumps Martha gave
Tail command prints last 10 lines of nohup.out so that we can see which point it is on!

## File Overview

The importers are structured by source, so we have some lucid and siemens importers, that work similarly but are catered to their own unique csv inputs.  

The siemens csv files should be parsed into better format using the **siemens_parser** before being added to the db.  

The **siemens_reader** then reads the better csv files and adds points from given ones to the db.

The **database_connection** should remain fairly consistent as all it does is take in information to put into our database or gets information from our database.

The **data_object_holders** is classes for other files to be able to more easily access information.

The **resources** file gets csv files from our data folder.

The **table_enumerations** is a point source enumeration that corresponds to what the point sources identifiers are in our database.

The **lucid_data** is

The **lucid_parser** is

The **lucid_reader** is
