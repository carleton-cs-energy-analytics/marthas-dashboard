# API

## Routes:
Base Url: http://energycomps.its.carleton.edu/api/index.php

### /buildings
Lists all buildings. Each building is composed of a building name and id.
Example query: http://energycomps.its.carleton.edu/api/index.php/buildings

### /building/name
Returns a building name and id.
Example query: http://energycomps.its.carleton.edu/api/index.php/building/LDC

### /building/id/rooms
Lists all of a buildings rooms. Each room is composed of a room name and id.
Example query: http://energycomps.its.carleton.edu/api/index.php/building/3/rooms

### /building/id/points
Lists all of a buildings points. Each point is composed of a description, id, name, point source id (lucid vs Siemens), point type id (ex. 13 is for temperature), and the room id containing the point.
Example query: http://energycomps.its.carleton.edu/api/index.php/building/3/points

### /building/id/points/point_type_id
Lists all of a buildings points that have a point type equal to point type id. Each point is composed of a description, id, name, point source id (lucid vs Siemens), and point type id (ex. 13 is for temperature), and the room id containing the point.
Example query: http://energycomps.its.carleton.edu/api/index.php/building/3/points/13

### /point/name
Lists all information including return type, units, factor, and point type name for a given point.
Example query: http://energycomps.its.carleton.edu/api/index.php/point/BI.LAB.HW.TEMP

### /values/point/point_id/start/end
Lists all of a point values between start and end. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/point/528/2016-08-18/2017-08-19

### /values/point/point_id/timestamp
Returns a points value at timestamp. The value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/point/528/2016-08-18 00:45:00

### /values/building/building_id/start/end
Lists all of a buildings values between start and end. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/building/3/2016-08-18/2017-08-19

### /values/building/building_id/timestamp
Returns all of a buildings values at timestamp. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/building/3/2016-08-18 00:45:00

### /values/timestamp
Returns all values at timestamp. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/2016-08-18 00:45:00

### /values/building/building_id/start/end/type/point_type
Lists all of a buildings values between start and end for all points that have a type of point type. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/building/3/2016-08-18/2017-08-19/type/13

### /values/building/building_id/start/end/source/source_id
Lists all of a buildings values between start and end for all points that have a source of source_id, eg 1 for lucid. Each value is composed of a timestamp, a value, a return type, a factor, a point id, and a point type id.
Example query: http://energycomps.its.carleton.edu/api/index.php/values/building/3/2016-08-18/2017-08-19/source/1
