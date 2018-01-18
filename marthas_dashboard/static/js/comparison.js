var add_comparison = document.getElementsByClassName("add-comparison")[0];
var close_comparison = document.getElementsByClassName("close-comparison")[1];
var comparison = document.getElementsByClassName("comparison")[0];
var forms = document.getElementsByClassName("filter_data");
var building_select = document.getElementsByClassName("building_select");
console.log(building_select)

add_comparison.addEventListener('click', function(event){
    comparison.style.display = 'block';
    add_comparison.style.display = 'none';
});
close_comparison.addEventListener('click', function(event){
    comparison.style.display = 'none';
    add_comparison.style.display = 'block';
});
for(var i = 0; i < forms.length; i++){
    forms[i].addEventListener("submit", constructComparisonUrl);
    building_select[i].addEventListener('change', buildingChange);
}
function constructComparisonUrl(event){
    event.preventDefault();
    var inputs = '?'
    console.log(forms)
    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var form_inputs = form.getElementsByTagName("input");
        var form_selects = form.getElementsByTagName("select");

        for(var j = 0; j < form_inputs.length; j++){
            inputs = inputs + addInputUrl(form_inputs[j])
        };
        for(var j = 0; j < form_selects.length; j++){
            inputs = inputs + addInputUrl(form_selects[j])
        };
        // get all elements
    };
    window.location.href = window.location.protocol + "//" + window.location.host + "/search"+inputs; 
}
function addInputUrl(el){
    return el.name+'='+el.value+'&';
}

// when the building changes we want to be able to update the possible point and room values in the selects
// so they can't select a room that isn't in their chosen building
function buildingChange(){
    var building_id = this.options[this.selectedIndex].value;
    // get the select input for this form
    point_selector = document.getElementsByName(this.form.name+'_point')[0];
    
    // get rid of all of our current point options
    while (point_selector.options.length > 0) {                
        point_selector.remove(0);
    } 
    // and add in the new ones according to our json values
    points = rooms_points[building_id]['points']
    Object.keys(points).forEach(function(key) {
        console.log(points[key])
        point_selector.options[point_selector.options.length]= new Option(points[key], key);
    });

    // will need to do the same thing for rooms at some point in the future 
    // but this should give a good example for how to do so
    // if unclear just ask me (jack)
}