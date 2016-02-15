$(document).ready(function(){

  function scrollToAnchor(aid){
    var aTag = $("#" + aid);
    $('html,body').animate({scrollTop: aTag.offset().top},'slow');
  }    

  $("#cr-download-button").click(function(){ 
    scrollToAnchor("cr-download");
  });
});

