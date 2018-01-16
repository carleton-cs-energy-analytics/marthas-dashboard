var button = document.getElementsByClassName("add-comparison");
var comparison = document.getElementsByClassName("comparison")[0];
button.addEventListener('click', function(event){
    comparison.style.display = 'block';
});

