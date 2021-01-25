$(document).ready(function(){
    $('.tech-slideshow').hide();
    $('.generate-button').hide();
    $('.image-editor').hide();
    $('#logodiv').click(function(){
        $('#logodiv').fadeTo('slow', 0.3);
        $('.tech-slideshow').show('slow');
        $('.generate-button').fadeIn('slow');
    });

    $('#button, #button-icon').click(function(){
        $('.generate-button').fadeOut();
        $('.generate-button').remove();
        
        $('.image-editor').fadeIn();
        
    });

    $('.image-editor').on('webkitAnimationEnd oanimationend msAnimationEnd animationend', function (e) {
        $.get('http://0.0.0.0:5000/generate', function (response) {
            let fileSrc = 'http://0.0.0.0:5000/generated/' + response + '/image0000.png';
            let image = $("#image");
            image.fadeOut('fast', function () {
            image.attr('src', fileSrc);
            image.css({
                "box-shadow": "0 4px 6px #000",
                "height": "50%",
                "width": "50%"
            });
            image.fadeIn('fast');
            });
        })
    })

    // TODO: slider dlugiej szerokosci i na koncu powtorzenie pierwszych

    var dir = "images/generated_images/";
    var fileextension = ".png";
    $moverL = $('#mover-left');
    $moverR = $('#mover-right');
    $.ajax({
        //This will retrieve the contents of the folder if the folder is configured as 'browsable'
        url: dir,
        success: function (data) {
            //List all .png file names in the page
            var images = $(data).find("a:contains(" + fileextension + ")");
            images.each(function (i) {
                var filename = this.href.replace(window.location.host, "").replace("http://", "");
                if (i < images.length/2) {
                    $moverL.append("<img src='" + dir + filename + "'>");
                } else if (i < images.length) {
                    $moverR.append("<img src='" + dir + filename + "'>");
                } else {
                    return false;
                }
            });
        }
    });

    $moverL.on('webkitAnimationIteration oanimationiteration msAnimationIteration animationiteration', function (e) {
        var overflowedImg = $moverL.children(":first");
        overflowedImg.appendTo($moverL);
    })

    $moverR.on('webkitAnimationIteration oanimationiteration msAnimationIteration animationiteration', function (e) {
        var overflowedImg = $moverR.children(":last");
        overflowedImg.prependTo($moverR);
    })


});