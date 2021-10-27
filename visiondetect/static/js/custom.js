$(document).ready(function (){
    let url_now = window.location.href;
    if(url_now.includes('objetos')){
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
});