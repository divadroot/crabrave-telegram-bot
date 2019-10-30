var base_url = "http://crabrave.codebucket.de/video/";

$("#generator").submit(function(event) {
    event.preventDefault();

    var overlay_text = $("#inputText").val();
    var style = $("#inputStyle").val();
    var font = $("#inputFont").val();
    var size = $("#inputSize").val();
    var color = $("#inputColor").val();
    var filter = $("#inputFilter").val();

    var file_url = base_url + encodeURI(overlay_text.replace("\\n", "\n")) + ".mp4";
    var video_url = file_url + "?style=" + style +
        "&font=" + font +
        "&size=" + size +
        "&color=" + color +
        "&filter=" + filter;

    console.log(video_url);

    $("#btnSubmit").attr("disabled", true);
    $("#btnSubmit").text("Generating video...");

    $.get(video_url, function(data) {
        $("#generator").hide();
        $("#result").show();

        $("#preview source").attr('src', video_url);
        $("#preview")[0].load();
        $("#preview")[0].play();

        $("#inputUrl").val(video_url);
    }).fail(function() {
        $("#error").fadeIn();
        setTimeout(function() {
            $("#error").fadeOut();
        }, 5000);
    }).always(function() {
        $("#btnSubmit").attr("disabled", false);
        $("#btnSubmit").text("Generate video");
    });
});

$("#btnCopy").click(function(event) {
    $("#inputUrl").select();
    $("#inputUrl")[0].setSelectionRange(0, 99999);
    document.execCommand("copy");
});

$("#btnBack").click(function(event) {
    $("#preview")[0].pause();
    $("#result").hide();
    $("#generator").show();
    $("#generator")[0].reset();
});

$("[data-hide]").on("click", function() {
    $("." + $(this).attr("data-hide")).fadeOut()
})