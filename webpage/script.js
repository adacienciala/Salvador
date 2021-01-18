$(document).ready(function(){
    $('.tech-slideshow').hide();
    $('#logodiv').click(function(){
        $('#logodiv').fadeTo('slow', 0.3);
        $('.tech-slideshow').show('slow');
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
            // document.querySelector('head').innerHTML += `<style>@keyframes moveSlideshowLeft {
            //     100% { 
            //         transform: translateX(calc(-128px * ${images.length/2}))
            //     }
            //   }</style>`;
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

    // function wrap() {
    //     setTimeout(function() {
    //         var overflowedImg = $moverL.children(":first");
    //         overflowedImg.appendTo($moverL);
    //         setTimeout(function() {
    //             wrap();
    //         }, 200);
    //     }, 800);
    // }

    // wrap();

    $moverL.on('animationiteration', function (e) {
        var overflowedImg = $moverL.children(":first");
        overflowedImg.appendTo($moverL);
    })

    $moverR.on('animationiteration', function (e) {
        var overflowedImg = $moverR.children(":last");
        overflowedImg.prependTo($moverR);
    })

    // setInterval(function() {
    //     var overflowedImg = $moverL.children(":first");
    //     overflowedImg.remove();
    //     overflowedImg.appendTo($moverL);
    //     console.log("moved");
    // }, 2000);
});