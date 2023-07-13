L.opmsLayer = (L.Layer ? L.Layer : L.Class).extend({

  //    options: {
  //        opacity: 0.5,
  //        maxZoom: 18,
  //        cellSize: 1,
  //        exp: 2,
  //        max: 2
  //    }

  initialize: function(latlngs, options) {
    this._latlngs = latlngs;
    // dataType: 2 => pm2.5, 3 => temperature, 4 => humidity
    L.setOptions(this, options);
  },

  setLatLngs: function(latlngs) {
    this._latlngs = latlngs;
    return this.redraw();
  },

  addLatLng: function(latlng) {
    this._latlngs.push(latlng);
    return this.redraw();
  },

  setOptions: function(options) {
    L.setOptions(this, options);
    if (this._colormap) {
      this._updateOptions();
    }
    return this.redraw();
  },

  redraw: function() {
    if (this._colormap && !this._frame && !this._map._animating) {
      this._frame = L.Util.requestAnimFrame(this._redraw, this);
    }
    return this;
  },

  onAdd: function(map) {
    this._map = map;

    if (!this._canvas) {
      this._initCanvas();
    }

    map._panes.overlayPane.appendChild(this._canvas);

    map.on('moveend', this._reset, this);

    if (map.options.zoomAnimation && L.Browser.any3d) {
      map.on('zoomanim', this._animateZoom, this);
    }

    this._reset();
  },

  onRemove: function(map) {
    map.getPanes().overlayPane.removeChild(this._canvas);

    map.off('moveend', this._reset, this);

    if (map.options.zoomAnimation) {
      map.off('zoomanim', this._animateZoom, this);
    }
  },

  addTo: function(map) {
    map.addLayer(this);
    return this;
  },

  _initCanvas: function() {
    var canvas = this._canvas = L.DomUtil.create('canvas', 'leaflet-colormap-layer leaflet-layer');

    var originProp = L.DomUtil.testProp(['transformOrigin', 'WebkitTransformOrigin', 'msTransformOrigin']);
    canvas.style[originProp] = '50% 50%';

    var size = this._map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;

    var animated = this._map.options.zoomAnimation && L.Browser.any3d;
    L.DomUtil.addClass(canvas, 'leaflet-zoom-' + (animated ? 'animated' : 'hide'));

    this._colormap = colormap(canvas);
    this._updateOptions();
  },

  _updateOptions: function() {
    this._colormap.cellSize(this.options.cellSize || this._colormap.defaultCellSize);
    if (this.options.maxVal) {
      this._colormap.max(this.options.maxVal);
    }
    if (this.options.minVal) {
      this._colormap.min(this.options.minVal);
    }
    if (this.options.gradient) {
      this._colormap.gradient(this.options.gradient);
    }
    
  },

  _reset: function() {
    var topLeft = this._map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(this._canvas, topLeft);

    var size = this._map.getSize();

    if (this._colormap._width !== size.x) {
      this._canvas.width = this._colormap._width = size.x;
    }
    if (this._colormap._height !== size.y) {
      this._canvas.height = this._colormap._height = size.y;
    }

    this._redraw();
  },

  _redraw: function() {
    if (!this._map) {
      return;
    }
    var data = [],
      // r is cell size
      r = this._colormap._r,
      // screen size: o.Point {x: 1156, y: 983}
      size = this._map.getSize(),
      // bounds of pixel coordinate on the screen
      bounds = new L.Bounds(
        L.point([-r, -r]),
        size.add([r, r])
      ),
      // exp used for weighting, 1 by default
      // exponential distances of the n data points to the estimated point
      exp = this.options.exp || 2,
      maxZoom = this.options.maxZoom === undefined ? this._map.getMaxZoom() : this.options.maxZoom,
      cellCen = r / 2,
      // number of cells on the x-axis of the screen
      nCellX = Math.ceil((bounds.max.x - bounds.min.x) / r) + 1,
      // number of cells on the y-axis of the screen
      nCellY = Math.ceil((bounds.max.y - bounds.min.y) / r) + 1,
      numberOfData = this._latlngs.length, 
      // dataType: 2 => pm2.5, 3 => temperature, 4 => humidity
      dataType = this.options.dataType || 2,
      // station effective range in km
      station_range = this.options.station_range || 10,
      maxVal = this.options.maxVal || 150.0,
      minVal = this.options.minVal || 0.0;
    console.log("Zoom level:", map.getZoom());
    console.log("Cells:", nCellY * nCellX);
    console.log("Data points:", this._latlngs.length);

    // -- cclljj
    // left top lat lon coordinate of the screen
    var leftTop = map.containerPointToLatLng([0, 0]),
      // right bottom lat lon coordinate of the screen
      rightBottom = map.containerPointToLatLng([map.getSize().x, map.getSize().y]),
      // km per pixel on x-axis
      offsetX = Math.abs(leftTop.lng - rightBottom.lng) * 104.64 / map.getSize().x,
      // km per pixel on y-axis
      offsetY = Math.abs(leftTop.lat - rightBottom.lat) * 110.69 / map.getSize().y

    // Inverse Distance Weighting (IDW)
    //       Σ (1 / (di ^ p)) * vi
    // V = -------------------------
    //          Σ (1 / (di ^ p))
    // Reference:
    // http://www.gitta.info/ContiSpatVar/de/html/Interpolatio_learningObject2.xhtml
    
    // cellsn = Σ (1 / (di ^ p)) * vi
    // cellsd = Σ (1 / (di ^ p))
    var cellsn = new Array(nCellY),
      cellsd = new Array(nCellY);
    // initialize cellsn and cellsd to 0
    for (var i = 0; i < nCellY; i++) {
      cellsn[i] = new Array(nCellX);
      cellsd[i] = new Array(nCellX);
      for (var j = 0; j < nCellX; j++) {
        cellsn[i][j] = 0;
        cellsd[i][j] = 0;
      }
    }

    // 10 km per degree
    let tenKmPerLng = 10 / 104.64;
    let tenKmPerLat = 10 / 110.69;
    // limit the coordinate
    leftTop.lat += tenKmPerLat
    leftTop.lng -= tenKmPerLng;
    rightBottom.lat -= tenKmPerLat;
    rightBottom.lng += tenKmPerLng;
    let pointCounter = 0;
    console.time("process colormap in bounds");
    for (var k = 0; k < numberOfData; k++) {
      // check whether IDW value is valid
      if(isNaN(this._latlngs[k][dataType])
        || this._latlngs[k][dataType] > maxVal
        || this._latlngs[k][dataType] < minVal) {
        // console.log("malfunction station: ", this._latlngs[k]);
        continue;
      }
      // eliminate data outside the screen
      if(this._latlngs[k][0] > leftTop.lat ||
         this._latlngs[k][0] < rightBottom.lat ||
         this._latlngs[k][1] < leftTop.lng ||
         this._latlngs[k][1] > rightBottom.lng) {
        continue;
      }
      pointCounter++;
      // p is the pixel coordinate of _latlngs[k] on the screen
      var p = this._map.latLngToContainerPoint(L.latLng(this._latlngs[k][0], this._latlngs[k][1])),
        // left pixel coordinate of the cell
        x1 = p.x - station_range / offsetX,
        // right
        x2 = p.x + station_range / offsetX,
        // top
        y1 = p.y - station_range / offsetY,
        // bottom
        y2 = p.y + station_range / offsetY;

      // cell coordinate
      x1 = Math.round(x1 / r + 0.5);
      x2 = Math.ceil(x2 / r - 0.5);
      y1 = Math.round(y1 / r + 0.5);
      y2 = Math.ceil(y2 / r - 0.5);

      // check if x1, x2, y1, y2 out of cellsn, cellsd bounds
      if (x2 < 0) {
        continue;
      }
      if (x1 >= nCellX) {
        continue;
      }
      if (y2 < 0) {
        continue;
      }
      if (y1 >= nCellY) {
        continue;
      }

      if (x1 < 0) {
        x1 = 0;
      }
      if (x2 >= nCellX) {
        x2 = nCellX - 1;
      }
      if (y1 < 0) {
        y1 = 0;
      }
      if (y2 >= nCellY) {
        y2 = nCellY - 1;
      }
      // L.marker([this._latlngs[k][0], this._latlngs[k][1]]).addTo(map);
      // calculate every point effect by the station
      for (var j = x1; j <= x2; j++) {
        for (var i = y1; i <= y2; i++) {
          if (cellsd[i][j] < 0.0) {
            // center of the cell
            // cellsd = -1
            continue;
          }
          // estimated point pixel coordinate
          var cp = L.point((j * r + cellCen), (i * r + cellCen));

          // distance in km on x-axis
          var LJ_x = (p.x - cp.x) * offsetX;
          // distance in km on y-axis
          var LJ_y = (p.y - cp.y) * offsetY;
          var LJ_dist = Math.sqrt(LJ_x * LJ_x + LJ_y * LJ_y);
          if (LJ_dist > station_range) {
            // point out of effective range
            continue;
          }

          // IDW value
          var val = this._latlngs[k][dataType];
          // pixel distance
          var distInPixels = cp.distanceTo(p);

          if (distInPixels === 0.0) {
            // cell center fills in original value
            cellsn[i][j] = val;
            cellsd[i][j] = -1;
          } else {
            var distInPixelsExp = Math.pow(distInPixels, exp);
            cellsn[i][j] += (val / distInPixelsExp);
            cellsd[i][j] += (1.0 / distInPixelsExp);
          }
        }
      }
    }
    console.log("Points for colormap:", pointCounter);
    for (var i = 0; i < nCellY; i++) {
      for (var j = 0; j < nCellX; j++) {
        if (cellsd[i][j] < 0.0) {
          cellsd[i][j] = 1.0;
        }
        var interpolVal = 0.0
        if (cellsd[i][j] === 0.0) {
          // cell not used
          interpolVal = minVal - 1;
        } else {
          interpolVal = cellsn[i][j] / cellsd[i][j];
        }
        // IDW value
        var cell = [
          Math.round(j * r), 
          Math.round(i * r), 
          Math.min(interpolVal, maxVal)
        ];

        if (cell !== undefined) {
          data.push(cell);
        }
      }
    }
    console.timeEnd("process colormap in bounds");
    console.time("draw");
    this._colormap.data(data).draw(this.options.opacity);
    console.timeEnd("draw");
    this._frame = null;
  },

  _animateZoom: function(e) {
    var scale = this._map.getZoomScale(e.zoom),
      offset = this._map._getCenterOffset(e.center)._multiplyBy(-scale).subtract(this._map._getMapPanePos());

    if (L.DomUtil.setTransform) {
      L.DomUtil.setTransform(this._canvas, offset, scale);

    } else {
      this._canvas.style[L.DomUtil.TRANSFORM] = L.DomUtil.getTranslateString(offset) + ' scale(' + scale + ')';
    }
  }
});

L.opmsLayer = function(latlngs, options) {
  return new L.opmsLayer(latlngs, options);
};
