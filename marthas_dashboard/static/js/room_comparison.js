var comparison_rows = document.getElementsByClassName("room-comparison-row");

if (comparison_rows.length > 0){
    comparison_rows = comparison_rows[0];
    comparison_rows.addEventListener("click", constructRoomInspectorURL);
}

function constructRoomInspectorURL(e){

    var data = {};
    var target = e.srcElement || e.target;
    while (target && target.nodeName !== "TR") {
        target = target.parentNode;
    }
    if (target) {
        var cells = target.getElementsByTagName("td");
        // Create a tuple of html (headers, value) information
        for (var i = 0; i < cells.length; i++) {
            var header = cells[i].headers;
            var value = cells[i].innerHTML;
            data[header] = value;
        }
    }

    data["date"]= document.getElementById("date_select").value;
    data["timestamp"] = document.getElementById("timestamp_select").value;
    data["building"] = document.getElementById("building_select").value;

    var inputs = '?';

    for (const key in data) {
        value = data[key];
        inputs = inputs + addInputUrl(key, value);
    }

    window.location.href = window.location.protocol + "//" + window.location.host + "/room-inspector" + inputs;

}
function addInputUrl(header, value){

    return header + '=' + value +'&';
}