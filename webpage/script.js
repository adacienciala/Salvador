$(document).ready(function(){
    $('.tech-slideshow').hide();
    $('.generate-button').hide();
    $('#logodiv').click(function(){
        $('#logodiv').fadeTo('slow', 0.3);
        $('.tech-slideshow').show('slow');
        $('.generate-button').fadeIn('slow');
    });

    $('#button, #button-icon').click(function(){
        console.log("click");
    });

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