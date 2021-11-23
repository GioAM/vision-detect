$(document).ready(function (){
    let url_now = window.location.href;
    if(url_now.includes('objeto')){
        $('#objetos').removeClass('link-dark').addClass('link-secondary');
    }else if(url_now.includes('camera')){
        $('#camera').removeClass('link-dark').addClass('link-secondary');
    }else if(url_now.includes('treinamento')){
        $('#treinamento').removeClass('link-dark').addClass('link-secondary');
    }else if(url_now.includes('deteccao')){
        $('#deteccao').removeClass('link-dark').addClass('link-secondary');
    }else if(url_now.includes('about')){
        $('#about').removeClass('link-dark').addClass('link-secondary');
    }else{
        $('#home').removeClass('link-dark').addClass('link-secondary');
    }
    $('#ip').mask('099.099.099.099');
    $('#add-image-form').hide();
});
$("#select-add-image").on("change", function(){
    if (this.value.includes("input")) {
        $('#add-image-form').show();
        $('#new-image-camera').hide();
    }else if(this.value.includes("camera")){
        $('#add-image-form').hide();
        $('#new-image-camera').show();
    }
});

$('#detect-objeto').on('click', function (){
   $.ajax({
        url: 'http://localhost:8000/detect/objects',
        method: "GET",
        data: []
    }).then(function(data){
        document.getElementById('image-result').src = data['imagem'];
        drawTable(data['contagem']);
    });
});

function drawTable(contagem){
    contagem = jQuery.parseJSON(contagem);
    $('#contagem-objetos').html('');
    for(var k in contagem) {
        $('#contagem-objetos').append(
            `<tr>
              <td>${k}</td>
              <td>${contagem[k]}</td>
            </tr>`
        );
    }
}