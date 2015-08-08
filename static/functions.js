function getFileExtension(filename){
    return filename.split('.').pop();
}

function isimagefile(filename){
    var imgs=Array("png", "gif", "jpg", "bmp", "jpeg");
    ext=getFileExtension(filename);
    ext=ext.toLowerCase();

    return ($.inArray(ext, imgs)!=-1)
}

function ismusicfile(filename){
    var imgs=Array("mp3", "wma", "ogg", "aac");
    ext=getFileExtension(filename);
    ext=ext.toLowerCase();

    return ($.inArray(ext, imgs)!=-1)
}

function showpreview(file){
    $('#previewimage').html("<img class='img-responsive' src='/download?plik="+Base64.encode(file)+"' height=165 style='max-width:300px;'></img>");
}

function showmusicpreview(file){
    $('#previewmusic').html('<audio src="/audio?filename='+Base64.encode(file)+'"></audio>');
}

function selectfile(file){
    //set filename
    $('#filename').html(file);
    $("#fileinfo").html("");


    getfileinfo(file);

    if (isimagefile(file)){
        showpreview(file);
        $('#previewmusic').html('');
    }else if (ismusicfile(file)){
        showmusicpreview(file);
        createplayers();
    }else{
        $('#previewimage').html('')
        $('#uploadbar').hide('slow');
        $('#previewmusic').html('');
    }
    //set download button link
    $("#downlaodbutton").attr("href", "/download?plik="+Base64.encode(file));
}

function pastefoldericon(file){
    document.write("<img src='/static/icons/fm/foldericon.png'></img>");
}

function pastefileicon(file){
    if (ismusicfile(file)){
        document.write("<img src='/static/icons/fm/musicicon.png'></img>");
    }else if (isimagefile(file)){
        document.write("<img src='/static/icons/fm/imageicon.png'></img>");
    }else{
        document.write("<img src='/static/icons/fm/fileicon.png'></img>");
    }
}

function toggleupload(){
    if ($('#uploadbar').is(':visible')){
        $('#uploadbar').hide('slow');
    }else{
        $('#uploadbar').show('slow');
    }
}

function togglepreview(){
    if ($('#previewbar').is(':visible')){
        $('#previewbar').hide('slow');
    }else{
        $('#previewbar').show('slow');
    }
}

function getfileinfo(file){
    $("#fileinfo").load("/fileinfo?file="+Base64.encode(file));
}

function sendterminalcommand(){
    var text=$("#commandtext").val();
    if (text=="")return;
    //add text
    $("#terminalcontent").append("$ "+text+"<br/>");
    //get result
    var output=$.ajax({
          url: "/execute",
          type:'post',
          data:{'command':text},
          async: false
         }).responseText;
    //replace new lines
    output = output.replace(/</g, '&lt;');
    output = output.replace(/>/g, '&gt;');
    output = output.replace(/\n/g, '<br/>');
    output = output.replace(/ /g, '&nbsp;');
    output = output.replace(/\t/g, '&#9;');
    //add result
    $("#terminalcontent").append(output+"<br/>");

    //clear entry
    $("#commandtext").val("")
}

function triggerenter(){
    $("#commandtext").keyup(function(event){
    if(event.keyCode == 13){
        sendterminalcommand();
    }
});
}

function createplayers(){
    var players="";
    audiojs.events.ready(function(){
    players = audiojs.createAll();
  });
}

function addtoplaylist(){
    file=$('#filename').html();
    if (ismusicfile(file)){
        $.get("/addsong?file="+Base64.encode(file));
        alert("Song added to playlist");
    }
    else {
		alert("File is not music type")
	}
}

function removefromplaylist(index){
    $.get('/removesong?id='+index+'', function(data){
        document.location="/music";
    });

}

function songmove(index, movedown){
    $.get('/movesong?id='+index+'&down='+movedown, function(data){
        document.location="/music";
    });

}

function launchmusicplayer(path){
    $('#previewmusic').html("<audio src='/audio?path="+path+"'></audio>");
    players = audiojs.createAll({autoplay:true});
}

function hiddenfiles_docheck(){
    var checked=$('#hiddenfiles_check').prop('checked') ? 1:0;
    $.get("/sethiddenfiles?state="+checked);
}
