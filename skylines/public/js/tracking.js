

/**
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  for (fid in flights) {
    var url = '/tracking/' + flights[fid].sfid + '/json';

    $.ajax(url, {
      data: { last_update: flights[fid].last_update || null },
      success: function(data) {
        updateFlight(data.sfid, data.encoded.points, data.encoded.levels,
                     data.num_levels, data.barogram_t, data.barogram_h,
                     data.enl);

        initRedrawLayer(map.getLayersByName('Flight')[0]);
        updateBaroScale();
        updateBaroData();
      }
    });
  }
}

/**
 * Updates a tracking flight.
 *
 * Note: _lonlat, _levels, _time, _enl and _height MUST have the same number of
 *   elements when decoded.
 *
 * @param {int} tracking_id SkyLines tracking ID.
 * @param {String} _lonlat Google polyencoded string of geolocations
 *   (lon + lat, WSG 84).
 * @param {String} _levels Google polyencoded string of levels of detail.
 * @param {int} _num_levels Number of levels encoded in _lonlat and _levels.
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of enl values.
 */

function updateFlight(tracking_id, _lonlat, _levels, _num_levels, _time,
    _height, _enl) {
  var height = OpenLayers.Util.decodeGoogle(_height);
  var time = OpenLayers.Util.decodeGoogle(_time);
  var enl = OpenLayers.Util.decodeGoogle(_enl);
  var lonlat = OpenLayers.Util.decodeGooglePolyline(_lonlat);
  var lod = OpenLayers.Util.decodeGoogleLoD(_levels, _num_levels);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.

  if (lonlat.length < 2) return;

  var points = new Array();
  for (var i = 1, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
        transform(new OpenLayers.Projection('EPSG:4326'),
                  map.getProjectionObject()));
  }

  // find the flight to update
  var flight_id = -1;
  for (i in flights) {
    if (tracking_id == flights[i].sfid)
      flight_id = i;
  }

  if (flight_id == -1) return;

  var flot_h = [], flot_enl = [];
  for (var i = 0; i < time.length; i++) {
    var timestamp = time[i] * 1000;
    flot_h.push([timestamp, height[i]]);
    flot_enl.push([timestamp, enl[i]]);
  }

  // update flight
  var flight = flights[flight_id];

  // points is already sliced
  flight.geo.components = flight.geo.components.concat(points);
  flight.geo.componentsLevel = flight.geo.componentsLevel.concat(lod.slice(1));
  flight.t = flight.t.concat(time.slice(1));
  flight.h = flight.h.concat(height.slice(1));
  flight.enl = flight.enl.concat(enl.slice(1));
  flight.lonlat = flight.lonlat.concat(lonlat.slice(1));
  flight.flot_h = flight.flot_h.concat(flot_h.slice(1));
  flight.flot_enl = flight.flot_enl.concat(flot_enl.slice(1));

  // recalculate bounds
  flight.geo.bounds = flight.geo.calculateBounds();
  // reset indices
  for (var i = 0, len = flight.geo.components.length; i < len; i++) {
    flight.geo.components[i].originalIndex = i;
  }

  flight.last_update = flight.t[flight.t.length - 1];

  setTime(global_time);
}
