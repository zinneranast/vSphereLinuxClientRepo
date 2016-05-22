$(document).ready(function() {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
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
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });


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


  $('.toggle-link').toggleClass('active');
  $('.toggle-link').next('.toggle-content').slideToggle(100);


  $('.toggle-link').on('click', function() {
    $(this).next('.toggle-content').slideToggle(100);
  });

  var vmid;
  var vmname;
  var prev2;
  $('.toggle-content').on('click', '.item', function() {
    vmid = $(this).data('vmid');
    vmname = $(this).data('vmname');
    if (prev2 != undefined) {
      prev2.removeClass('active');
    }
    $(this).addClass('active');
    prev2 = $(this);
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

  var prev4;
  $('.item-item span').on('click', function() {
    var $el = $(this).parent('.item-item');
    if($el.hasClass('active')) {
      $el.removeClass('active');
    } else {
      if(prev4 != undefined) {
        prev4.parent('.item-item').removeClass('active');
      }
      prev4 = $(this);
      $el.addClass('active');
    }
    prev4 = $(this);
  });

  $('.item-item').on('mouseover', function() {
    $(this).addClass('active');
  });

  $('.item-item').on('mouseout', function() {
    $(this).removeClass('active');
  });

    $('.item-item-item').on('mouseover', function() {
    $(this).addClass('active');
  });

  $('.item-item-item').on('mouseout', function() {
    $(this).removeClass('active');
  });


  $('.vm-state-start').on('click', function() {
    $(this).addClass('active');
    $.ajax({
      method: 'POST',
      url: '/vsphclient/startmachine/',
      data: {'machine_id': vmid, 'machine_name': vmname},
      success: function (data) {
        $('.toggle-content').html($(data).find('.toggle-content').html());
        $('.operation-history').html($(data).find('.operation-history').html());
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while starting virtual machine.");
      }
    });
  });

  $('.vm-state-stop').on('click', function() {
    $(this).addClass('active');
    $.ajax({
      method: 'POST',
      url: '/vsphclient/stopmachine/',
      data: {'machine_id': vmid, 'machine_name': vmname},
      success: function (data) {
        $('.toggle-content').html($(data).find('.toggle-content').html());
        $('.operation-history').html($(data).find('.operation-history').html());
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while stopping virtual machine.");
      }
    });
  });

  $('.vm-state-suspend').on('click', function() {
    $(this).addClass('active');
    $.ajax({
      method: 'POST',
      url: '/vsphclient/suspendmachine/',
      data: {'machine_id': vmid, 'machine_name': vmname},
      success: function (data) {
        $('.toggle-content').html($(data).find('.toggle-content').html());
        $('.operation-history').html($(data).find('.operation-history').html());
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
      data: {'machine_id': vmid, 'machine_name': vmname},
  	  success: function (data) {
        $('.toggle-content').html($(data).find('.toggle-content').html());
        $('.operation-history').html($(data).find('.operation-history').html());
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while reseting virtual machine.");
      }
    });
  });


  var take_snapshot_buttons = new Array();
  take_snapshot_buttons.push({
    text: 'Cancel',
    click: function() {
      $('.take-snapshot').removeClass('active');
      $(this).dialog('close');
    }
  });

  var snapshot_name;
  take_snapshot_buttons.push({
    text: 'OK',
    click: function() {
      $(this).removeClass('active');
      snapshot_name = $(this).data('snapshot_name');
      $.ajax({
        method: 'POST',
        url: '/vsphclient/takesnapshot/',
        data: $(this).serialize() + '&machine_id=' + vmid + '&machine_name=' + vmname,
        success: function (data) {
          $('.operation-history').html($(data).find('.operation-history').html());
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while creating snapshot.");
        }
      });
      $(this).dialog('close');
    }
  });

  $('#create-snapshot-form').dialog({
     autoOpen: false,
     buttons: take_snapshot_buttons
  });

  $('.take-snapshot').on('click', function (){
      $(this).addClass('active');
      $('#create-snapshot-form').dialog('open');
  });


  var revert_snapshot_buttons = new Array();
  revert_snapshot_buttons.push({
    text: 'Cancel',
    click: function() {
      $(this).removeClass('active');
      $(this).dialog('close');
    }
  });

  revert_snapshot_buttons.push({
    text: 'OK',
    click: function() {
      $(this).removeClass('active');
      $.ajax({
        method: 'POST',
        url: '/vsphclient/revertsnapshot/',
        data: {'machine_id': vmid, 'machine_name': vmname},
        success: function (data) {
          $('.operation-history').html($(data).find('.operation-history').html());
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while reverting the virtual machine to the current snapshot.");
        }
      });
      $(this).dialog('close');
    }
  });

  $('#revert-snapshot-form').dialog({
      autoOpen: false,
      buttons: revert_snapshot_buttons
    });

  $('.revert-snapshot').on('click', function() {
    $(this).addClass('active');
    $('#revert-snapshot-form').dialog('open');
  });


  var manager_snapshot_buttons = new Array();
  manager_snapshot_buttons.push({
    text: 'Cancel',
    click: function() {
      $(this).removeClass('active');
      $(this).dialog('close');
    }
  });

  manager_snapshot_buttons.push({
    text: 'OK',
    click: function() {
      $(this).removeClass('active');
      $(this).dialog('close');
    }
  });

  $('#manager-snapshot-form').dialog({
      autoOpen: false,
      buttons: manager_snapshot_buttons
  });

  $('.manager-snapshot').on('click', function() {
    $(this).addClass('active');
    $.ajax({
        method: 'POST',
        url: '/vsphclient/managersnapshot/',
        data: {'machine_id': vmid, 'machine_name': vmname},
        success: function (data) {
          $('.snapshot-info').html(data);
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while getting information about snapshots.");
        }
      });
    $('#manager-snapshot-form').dialog('close');
  });  
});
