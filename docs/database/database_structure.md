# Database Structure

## Database Creation

Run  ```V1_createTables.sql``` on our database.  

## Database Restart
Run ```Oopsies.sql``` which will delete everything and start us over.  Beware of oopsies and make sure you really want to reset and not just delete a specific building.  Adding the historical data takes a while, so just be cautious.

## Database Structure
We have multiple tables: buildings, rooms, point types, point sources, points, and point values.

* **Building**
  * ID
  * Name
* **Rooms**
  * ID
  * Name
  * BuildingID
* **PointTypes**
  * ID
  * Name
  * Units
  * ReturnType
  * Factor
  * Description
* **EquipmentBoxes**
  * ID
  * Name
  * Description
* **PointSources**
  * ID
  * Name
* **Points**
  * ID
  * Name
  * RoomID
  * PointSourceID
  * PointTypeID
  * EquipmentID
  * Description
* **PointValues**
  * PointTimestamp
  * PointID
  * PointValue

Everything that is of the form _ _ ID is a reference to another table.
* A pointvalue has a point.
* A point has a room, pointsource, equipmentbox, and pointtype.
* A room has a building.

## Explanation of Database Structure
Every point we get has a name like "EV.RM103.V" which stands for one measurement.
Using this name we can get information like what building and room it is in, if it is in a larger piece of equipment, if it is a numerical or enumerated (on/off) measurement, what units it has, and some human readable description for it. 

### Point types table
Most of that information gets its own table, but the point types table has a lot of the information about what we can expect out of the value.
ReturnType tells us whether we should expect a float (numerical) or enumerate (on/off, high/medium/low) value. 
* If it is a float, 
  * Units tells us what units that float represents (degrees F, angle open).
  * Factor tells us how far to the left we should move the decimal (multiple by 10^factor) when we take the value out of the table - this is used to make every PointValue an integer
* If it is enumerated,
  * units tells us what the indices in the PointValues table's PointValue column should be interpreted as (0 = OFF, 1 = ON).
  * Factor is null


## SQL Queries You May Enjoy

### Count all point values for a given building, helpful to see if importing a building is going well!

```sql
SELECT count(pointtimestamp) as count, pointid, array_agg(pointvalue) as point_values, points.name as point_name, Rooms.name as room_name,
  buildings.name as building_name, pointsources.name as point_source, pointtypes.factor as factor, pointtypes.returntype as return_type,
  points.description as description
FROM PointValues
JOIN Points on PointValues.pointID = Points.ID
JOIN Rooms on Points.RoomID = Rooms.ID
JOIN Buildings on Rooms.BuildingID = Buildings.ID
JOIN pointsources on points.pointsourceid = pointsources.id
JOIN pointtypes on points.pointtypeid = pointtypes.id
  WHERE buildings.name = 'Hulings'
GROUP BY pointid, point_name, room_name, building_name, point_source, factor, return_type, description;
```

### Group PointValues by Timestamp, get pointname and value

```sql
SELECT pointtimestamp, ('{' || string_agg('"' || points.name || '": ' || pointvalue, ',') || '}')::json as activity
FROM pointvalues
  JOIN points on pointvalues.pointid = points.id
GROUP BY pointtimestamp;
```
