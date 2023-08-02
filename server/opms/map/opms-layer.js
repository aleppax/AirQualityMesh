L.opmsLayer = L.GridLayer.extend({
    
    createTile: function(coords){
        // create a <canvas> element for drawing
        var tile = L.DomUtil.create('canvas', 'leaflet-tile');

        // setup tile width and height according to the options
        var size = this.getTileSize();
        tile.width = size.x;
        tile.height = size.y;

        // get a canvas context and draw something on it using coords.x, coords.y and coords.z
        var ctx = tile.getContext('2d');
        
        // draw
        ctx.globalAlpha = this.options.opacity;
        let cellsX = tile.width/this.options.cellSize;
        let cellsY = tile.height/this.options.cellSize;
        for (let i = 0; i < cellsX; i++) {
            for (let j = 0; j < cellsY; j++) {
                //let coordinates = this._map.layerPointToLatLng(this._map.layerPointToContainerPoint(L.point(j * this.options.cellSize, i * this.options.cellSize)));
                let nwPoint = coords.scaleBy(size).add(L.point(j * this.options.cellSize, i * this.options.cellSize));
                let coordinates = this._map.unproject(nwPoint, coords.z);
                //let coordinates = this._map.layerPointToLatLng(nwPoint);
                if (this.options.bounds.contains(coordinates)) {
                    // assign color to value
                        let cval = Math.floor(Math.random() * 10) * 2;
                        ctx.fillStyle = this.options.gradient[cval];
                        ctx.fillRect(j * this.options.cellSize+4, i * this.options.cellSize+4, this.options.cellSize-4, this.options.cellSize-4);
                }
            }
        }

        // return the tile so it can be rendered on screen
        return tile;
    },
    computeCell: function(coords) {
        return 8;
    }
});
