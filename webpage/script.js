$(document).ready(function(){
    $('.tech-slideshow').hide();
    $('#logodiv').click(function(){
        $('#logodiv').fadeTo('slow', 0.3);
        $('.tech-slideshow').show('slow');
    });

    var dir = "images/generated_images/";
    var fileextension = ".png";
    var imgSize = 128; // px
    $.ajax({
        //This will retrieve the contents of the folder if the folder is configured as 'browsable'
        url: dir,
        success: function (data) {
            var maxEl = $(window).width() / imgSize;
            console.log(maxEl);
            $moverL = $('#mover-left');
            $moverR = $('#mover-right');
            //List all .png file names in the page
            $(data).find("a:contains(" + fileextension + ")").each(function (i) {
                var filename = this.href.replace(window.location.host, "").replace("http://", "");
                if (i < maxEl-2) {
                    $moverL.append("<img src='" + dir + filename + "'>");
                } else if (i < 2*maxEl-3) {
                    $moverR.append("<img src='" + dir + filename + "'>");
                } else {
                    return false;
                }
                console.log(i, maxEl);
            });
        }
    });
});