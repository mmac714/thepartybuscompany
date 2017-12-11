$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });

        // if dismiss or overlay was clicked
    $('#dismiss, .overlay').on('click', function () {
    	// hide the sidebar
    	$('#sidebar').removeClass('active');
    	// fade out the overlay
    	$('.overlay').fadeOut();
    });

    // when opening the sidebar
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $(this).toggleClass('active');
    });
}); 