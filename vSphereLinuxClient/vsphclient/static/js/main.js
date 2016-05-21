$('.vm-state-start').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.vm-state-start').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.vm-state-stop').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.vm-state-stop').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.vm-state-suspend').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.vm-state-suspend').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.vm-state-reset').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.vm-state-reset').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.take-snapshot').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.take-snapshot').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.revert-snapshot').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.revert-snapshot').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

$('.manager-snapshot').on('mouseover', function() {
        $(this).addClass('active-mouse');
});

$('.manager-snapshot').on('mouseout', function() {
        $(this).removeClass('active-mouse');
});

var vmid;
var prev2;
$('.item').on('click', function() {
        vmid = $(this).data('vmid');
	console.log(vmid);
        if (prev2 != undefined) {
                prev2.removeClass('active');
        }
        $(this).addClass('active');
        prev2 = $(this);
});

$('.toggle-link').on('click', function() {
        $(this).toggleClass('active');
        $(this).next('.toggle-content').slideToggle(100);
});

var prev3;
$('.menu-item span').on('click', function() {
        var $el = $(this).parent('.menu-item');
        if($el.hasClass('active')) {
                $el.removeClass('active');
        } else {
                if(prev3 != undefined) {
                        prev3.parent('.menu-item').removeClass('active');
                }
                prev3 = $(this);
                $el.addClass('active');
        }
        prev3 = $(this);
});

$('.item-item').on('mouseover', function() {
        $(this).addClass('active');
});

$('.item-item').on('mouseout', function() {
        $(this).removeClass('active');
});

$('.vm-state-stop').on('click', function() {
        $(this).addClass('active');

        $.ajax({
          method: 'POST',
          url: '/vsphclient/stopmachine/',
          data: {'machine_id': vmid},
          success: function (data) {
              $(".command-history").append(data);
          },
          error: function (data) {
            alert("ERROR: Something was going wrong while stopping virtual machine.");
          }
        });
});

$('.vm-state-start').on('click', function() {
        $(this).addClass('active');

        $.ajax({
          method: 'POST',
          url: '/vsphclient/startmachine/',
          data: {'machine_id': vmid},
          success: function (data) {
              $(".command-history").append(data);
          },
          error: function (data) {
            alert("ERROR: Something was going wrong while starting virtual machine.");
          }
        });
});

$('.vm-state-suspend').on('click', function() {
        $(this).addClass('active');

        $.ajax({
          method: 'POST',
          url: '/vsphclient/suspendmachine/',
          data: {'machine_id': vmid},
          success: function (data) {
              $(".command-history").append(data);
          },
          error: function (data) {
            alert("ERROR: Something was going wrong while suspending virtual machine.");
          }
        });
});

$('.vm-state-reset').on('click', function() {
        $(this).addClass('active');

        $.ajax({
          method: 'POST',
          url: '/vsphclient/resetmachine/',
          data: {'machine_id': vmid},
	  success: function (data) {
              $(".command-history").append(data);
          },
          error: function (data) {
            alert("ERROR: Something was going wrong while reseting virtual machine.");
          }
        });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var buttons = new Array();
buttons.push({
    text: 'Cancel',
    click: function() {
	$('.take-snapshot').removeClass('active');
        $(this).dialog('close');
    }
});

var snapshot_name;
buttons.push({
    text: 'OK',
    click: function() {
        $('.take-snapshot').removeClass('active');
	console.log('before submit');
	snapshot_name = $(this).data('snapshot_name');
        console.log(snapshot_name);
    	$.ajax({
	    method: 'POST',
            url: '/vsphclient/takesnapshot/',
	    data: $(this).serialize() + '&machine_id=' + vmid,
            success: function (data) {
         	$(".command-history").append(data);
	    },
	    error: function (data) {
	        alert("ERROR: Something was going wrong while creating snapshot.");
	    }
	});
        $(this).dialog('close');
    }
});

$('#snapshot-form').dialog({
    autoOpen: false,
    buttons: buttons
});

$('.take-snapshot').on('click', function (){
    $(this).addClass('active');
    $('#snapshot-form').dialog('open');
});
