var add_comparison = document.getElementsByClassName("add-comparison")[0];
var close_comparison = document.getElementsByClassName("close-comparison")[1];
var comparison = document.getElementsByClassName("comparison")[0];
var forms = document.getElementsByClassName("filter_data");
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