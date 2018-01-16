var button = document.getElementsByClassName("add-comparison")[0];
var comparison = document.getElementsByClassName("comparison")[0];
var forms = document.getElementsByClassName("filter_data");
console.log(forms)
button.addEventListener('click', function(event){
    comparison.style.display = 'block';
});
for(var form in forms){
    form.addEventListener("submit", constructComparisonUrl());
}
function constructComparisonUrl(event){
    event.preventDefault();
    var prepend = ''
    var inputs = '?'
    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var form_inputs = form.getElementsByTagName("input");
        var form_selects = form.getElementsByTagName("input");

        for(var j = 0; j < form_inputs.length; j++){
            inputs = inputs + addInputUrl(prepend, form_inputs[j])
        };
        for(var j = 0; j < form_selects.length; j++){
            inputs = inputs + addInputUrl(prepend, form_selects[j])
        };
        // get all elements
        prepend = 'c_';
    };
    window.location.href = window.location.protocol + "//" + window.location.host + "/comparison"+inputs; 
}
function addInputUrl(prepend, el){
    return prepend+el.name+'='+el.value+'&';
}