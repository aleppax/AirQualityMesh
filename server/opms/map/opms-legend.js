//BSD 2-Clause License

//Copyright (c) 2019, Li-Pang Huang
//All rights reserved.

//Redistribution and use in source and binary forms, with or without
//modification, are permitted provided that the following conditions are met:

//1. Redistributions of source code must retain the above copyright notice, this
   //list of conditions and the following disclaimer.

//2. Redistributions in binary form must reproduce the above copyright notice,
   //this list of conditions and the following disclaimer in the documentation
   //and/or other materials provided with the distribution.

//THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
//AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
//IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
//DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
//FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
//DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
//SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
//CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
//OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
//OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

L.Control.opmsLegend = L.Control.extend({
  initialize: function(gradients, options) {
    this.gradients = this._transformGradient(gradients);
    this.unit = options.unit;
    L.Util.setOptions(this, options);
  },

  onAdd: function(map) {
    let container = L.DomUtil.create('div', 'opms-legend leaflet-control-layers'),
      gradesLabels = '',
      gradientsLength = this.gradients.length;
    let numLength = 0;
    for(let i = 0; i < gradientsLength; i++) {
      let length = this.gradients[i].key.toString().length;
      if(numLength < length) numLength = length;
    }
    // loop through our density intervals and 
    // generate a label with a colored square for each interval
    for(let i = 0; i < gradientsLength; i++) {
      let color = this.gradients[i].value;
        gradesLabels +=
          `<i style="background:${color};">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;` + 
          `${this._formatNumber(numLength, this.gradients[i].key)}`
          + `${(this.gradients[i + 1] ? '<br>' : '+<br>')}`;
    }
    container.innerHTML =
      `<div class="leaflet-control-layers-base">
        <table>
          <tr>
            <td>${gradesLabels}</td>
          </tr>
          <tr>
            <td>${this.unit}</td>
          </tr>
        </table>
      </div>`;

    return container;
  },
  _transformGradient: function(gradients) {
    let newGradients = [];
    for(let i in gradients) {
      newGradients.push({key: +i, value: gradients[i]});
    }
    return newGradients.sort((item1, item2) => {
      return +item1.key - +item2.key;
    });
  },
  _formatNumber: function(length, number) {
    let result = number.toString();
    let numLength = result.length;
    result = result.replace("-", `&ndash;`);
    if(numLength < length) {
      for(let i = 0; i < length - numLength; i++) {
        result = "&nbsp;&nbsp;" + result;
      }
    }
    return result;
  }
});

L.control.opmsLegend = function(gradients, options) {
  return new L.Control.opmsLegend(gradients, options);
};
