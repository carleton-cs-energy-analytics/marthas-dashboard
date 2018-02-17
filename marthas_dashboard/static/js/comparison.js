var add_comparison = document.getElementsByClassName("add-comparison");
var close_comparison = document.getElementsByClassName("close-comparison");
var comparison = document.getElementsByClassName("comparison")[1];
var forms = document.getElementsByClassName("filter_data");
var building_select = document.getElementsByClassName("building_select");
var color_picker = document.getElementsByClassName("color-picker");
if (add_comparison.length > 0) {
    add_comparison = add_comparison[0];
    add_comparison.addEventListener('click', function (event) {
        comparison.classList.toggle("hidden");
        add_comparison.style.display = 'none';
    });
}
if (close_comparison.length > 1) {
    close_comparison = close_comparison[1];
    close_comparison.addEventListener('click', function (event) {
        comparison.classList.toggle("hidden");
        add_comparison.style.display = 'block';
    });
}

if (color_picker.length > 0) {
    color_picker[0].addEventListener('change', constructComparisonUrl);
}
for (var i = 0; i < forms.length; i++) {
    forms[i].addEventListener("submit", constructComparisonUrl);
    building_select[i].addEventListener('change', buildingChange);
}
function constructComparisonUrl(event) {
    event.preventDefault();
    var inputs = '?';
    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var parent = form.parentElement.parentElement;
        if (parent.classList.contains("hidden")) {
            continue;
        }
        var form_inputs = form.getElementsByTagName("input");
        var form_selects = form.getElementsByTagName("select");

        for (var j = 0; j < form_inputs.length; j++) {
            inputs = inputs + addInputUrl(form_inputs[j]);
        }
        ;
        for (var j = 0; j < form_selects.length; j++) {
            inputs = inputs + addInputUrl(form_selects[j]);
        }
        ;
        // get all elements
    }
    ;
    if (color_picker.length > 0) {
        color_picker = color_picker[0];
        inputs = inputs + "color=" + color_picker.options[color_picker.selectedIndex].value;
    }
    window.location.href = window.location.protocol + "//" + window.location.host + window.location.pathname + inputs;
}
function addInputUrl(el) {
    return el.name + '=' + el.value + '&';
}

// when the building changes we want to be able to update the possible point and room values in the selects
// so they can't select a room that isn't in their chosen building
function buildingChange() {
    var building_id = this.options[this.selectedIndex].value;
    // get the select input for this form
    point_selector = document.getElementsByName(this.form.name + '_point')[0];

    // get rid of all of our current point options
    while (point_selector.options.length > 0) {
        point_selector.remove(0);
    }
    // and add in the new ones according to our json values
    points = rooms_points[building_id]['points']
    Object.keys(points).forEach(function (key) {
        point_selector.options[point_selector.options.length] = new Option(points[key], key);
    });

    // will need to do the same thing for rooms at some point in the future 
    // but this should give a good example for how to do so
    // if unclear just ask me (jack)
}
