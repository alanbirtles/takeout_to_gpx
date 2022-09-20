import ijson
import argparse
import datetime
import os
import math
import gpxpy

args = argparse.ArgumentParser()
args.add_argument('--source', help='Records.json from google takeout location history export', )
args.add_argument('--from', dest='from_time', type=datetime.datetime.fromisoformat, help='start time for export in YY-MM-DDTHH-MM-SS+00:00 format')
args.add_argument('--to', type=datetime.datetime.fromisoformat, help='end time for export in YY-MM-DDTHH-MM-SS+00:00 format')
args.add_argument('--dest', help='output filename')

args = args.parse_args()

file_size = os.path.getsize(args.source)
last_percentage = 0

gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

with open(args.source, 'rb') as f:
    for location in ijson.items(f, 'locations.item'):
        timestamp = datetime.datetime.fromisoformat(location['timestamp'].replace('Z', '+00:00'))
        percentage = math.floor(100 * f.tell() / file_size)
        if percentage != last_percentage:
            print(f'{percentage}%, {timestamp.isoformat()}')
            last_percentage = percentage
        if timestamp > args.to:
            break
        if timestamp > args.from_time:
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(location['latitudeE7'] / 10000000, 
                location['longitudeE7'] / 10000000, 
                time=timestamp,
                elevation=location['altitude'] if 'altitude' in location else None))

with open(args.dest, 'w') as f:
    f.write(gpx.to_xml())
