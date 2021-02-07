let maxGeneratingTime = 30

$(document).ready(function(){
    hide_main_content();
    load_welcome_button();
    load_image();
    load_sliders()
});

function hide_main_content() {
    $('.tech-slideshow').hide();
    $('.generate-button').hide();
    $('.image-editor').hide();
}

function load_welcome_button() {

    function show_welcome_button() {
        $('#logodiv').click(function(){
            $('#logodiv').fadeTo('slow', 0.3);
            $('.tech-slideshow').show('slow');
            $('.generate-button').fadeIn('slow');
        });
    }

    function load_image_editor() {
        $('#button, #button-icon').click(function(){
            $('.generate-button').remove();
            $('.image-editor').fadeIn();
        });
    }

    show_welcome_button();
    load_image_editor();
}

function load_image() {

    $('.image-editor').on('webkitAnimationEnd oanimationend msAnimationEnd animationend', function () {
        
        function run_timer() {
            if (!document.getElementById('image').src.includes('.gif')) return;
            if (typeof sec == 'undefined')
                sec = 0
            else sec++
            const text = `Estimated time: ~${maxGeneratingTime}s. Elapsed time: ${sec} s.`;
            if (sec === maxGeneratingTime) {
                const refreshP = document.createElement("p")
                const text = document.createTextNode('Request might have failed, consider refreshing. ☹️')
                refreshP.appendChild(text)
                document.getElementById('image-editor').appendChild(refreshP);
            }
            $('#estimated-time-counter').text(text)
            setTimeout(run_timer, 1000)
        }
        
        run_timer();
        $.get('https://pomodoro-salvadoro.herokuapp.com/generate', function (response) {
            let fileSrc = 'https://pomodoro-salvadoro.herokuapp.com/generated/' + response + '/image0000.png';
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
            load_download_btn();
        })
        
    })
}

function load_download_btn() {
    $('#image-editor').append("<div id='download-btn' alt='download button'>");
    $('#download-btn').click(function(){
        var link = document.createElement('a');
        link.href = $("#image").attr('src');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

function load_sliders() {
    let $moverL = $('#mover-left');
    let $moverR = $('#mover-right');

    function prepare_sliders() {
        const dir = "images/generated_images/";
        $.get('https://pomodoro-salvadoro.herokuapp.com/slider_images', function (response) {
            let fileList = []
            try {
                fileList = JSON.parse(response)
            } catch (e) { console.log('Errorek', e)}

            fileList.forEach(function (filename, i) {
                if (i < fileList.length / 2) {
                    $moverL.append("<img src='" + dir + filename + "' alt='AI generated background image'>");
                } else if (i < fileList.length) {
                    $moverR.append("<img src='" + dir + filename + "' alt='AI generated background image'>");
                } else {
                    return false;
                }
            });
        })
    }

    function run_sliders() {
        $moverL.on('webkitAnimationIteration oanimationiteration msAnimationIteration animationiteration', function (e) {
            let overflowedImg = $moverL.children(":first");
            overflowedImg.appendTo($moverL);
        })

        $moverR.on('webkitAnimationIteration oanimationiteration msAnimationIteration animationiteration', function (e) {
            let overflowedImg = $moverR.children(":last");
            overflowedImg.prependTo($moverR);
        })
    }

    prepare_sliders();
    run_sliders();
}