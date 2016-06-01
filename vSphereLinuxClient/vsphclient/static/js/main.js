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
    $('.vm-state-start').removeClass('active');
    $('.vm-state-stop').removeClass('active');
    $('.vm-state-suspend').removeClass('active');

    $.ajax({
        method: 'POST',
        url: '/vsphclient/index/',
        data: {},
        success: function (data) {
          $('.right-block').html($(data).find('.right-block').html());
        }
      });
  });

  var vmid;
  var vmname;
  var vmstate;
  var prev2;
  $('.toggle-content').on('click', '.item', function() {
    vmid = $(this).data('vmid');
    vmname = $(this).data('vmname');
    vmstate = $(this).data('vmstate');

    if(vmstate == "Powered on") {
      $('.vm-state-start').addClass('active');
      $('.vm-state-stop').removeClass('active');
      $('.vm-state-suspend').removeClass('active');
      $('.vm-state-reset').removeClass('active');
    }else if(vmstate == "Powered off") {
      $('.vm-state-stop').addClass('active');
      $('.vm-state-start').removeClass('active');
      $('.vm-state-suspend').removeClass('active');
      $('.vm-state-reset').removeClass('active');
    }else if(vmstate == "Suspend") {
      $('.vm-state-suspend').addClass('active');
      $('.vm-state-start').removeClass('active');
      $('.vm-state-stop').removeClass('active');
      $('.vm-state-reset').removeClass('active');
    }

    if (prev2 != undefined) {
      prev2.removeClass('active');
    }
    $(this).addClass('active');
    prev2 = $(this);

    $.ajax({
      method: 'POST',
      url: '/vsphclient/summary/',
      data: {'machine_id': vmid, 'machine_name': vmname, 'machine_state': vmstate},
      success: function (data) {
        $('.right-block').html($(data).find('.right-block').html());
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while reseting virtual machine.");
      }
    });
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

  $('.menu-list-item').on('click', function() {
    var subist = $(this).find('.menu-sublist');
    if ( subist.length ) {
      subist.addClass('active');
    }    
  });

  $(document).on('click', function(e){
    if( !$(e.target).hasClass('item-item') &&
      !$(e.target).hasClass('menu-list-item') ) {    
        $('.menu-item, .menu-sublist').each(function(){
          $(this).removeClass('active');
        });   
      }
  });


  $('.vm-state-start').on('click', function() {
    $(this).addClass('active');
    $('.operation-history tr:first-child .status').html('<th style="width: 133px;"><div class="meter"><span>complete</span></div></th>');
    console.log($('.operation-history tr:first-child .status'))
    $.ajax({
      method: 'POST',
      url: '/vsphclient/startmachine/',
      data: {'machine_id': vmid, 'machine_name': vmname},
      success: function (data) {
        $('.toggle-content').html($(data).find('.toggle-content').html());
        $('.operation-history').html($(data).find('.operation-history').html());
        $('.vm-state-start').removeClass('active');
        // $('.status').html('<th id="status" style="width: 133px;"><img src="{% static "img/complete.png" %}" id="image">Completed</th>');
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
        $('.vm-state-stop').removeClass('active');
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while stopping virtual machine.");
      }
    });
    $('.vm-state-start').removeClass('active');
    $('.vm-state-suspend').removeClass('active');
    $('.vm-state-reset').removeClass('active');
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
        $('.vm-state-suspend').removeClass('active');
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while suspending virtual machine.");
      }
    });
    $('.vm-state-start').removeClass('active');
    $('.vm-state-stop').removeClass('active');
    $('.vm-state-reset').removeClass('active');
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
        $('.vm-state-reset').removeClass('active');
      },
      error: function (data) {
        alert("ERROR: Something was going wrong while reseting virtual machine.");
      }
    });
    $('.vm-state-stop').removeClass('active');
  });


  var deploy_buttons = new Array();
  deploy_buttons.push({
    text: 'Cancel',
    click: function() {
      $('#topology-deploy').removeClass('active');
      $(this).dialog('close');
    }
  });

  var topology;
  deploy_buttons.push({
    text: 'OK',
    click: function() {
      $(this).removeClass('active');
      alert("The process was started. Please do not update the page until the configuration is deployed.");
      $.ajax({
        method: 'POST',
        url: '/vsphclient/deploy/',
        data: $(this).serialize() + '&topology_name=' + topology,
        success: function (data) {
          alert(data);
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while deploying the configuration.");
        }
      });
      $(this).dialog('close');
    }
  });

  $('#deploy-form').dialog({
     autoOpen: false,
     buttons: deploy_buttons
  });

  $('#topology-deploy').on('click', function (){
      $(this).addClass('active');
      $('#deploy-form').dialog('open');
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
          $('.take-snapshot').removeClass('active');
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
      $('.revert-snapshot').removeClass('active');
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
          $('.revert-snapshot').removeClass('active');
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
      $.ajax({
        method: 'POST',
        url: '/vsphclient/managersnapshot/',
        data: {'machine_id': vmid, 'machine_name': vmname},
        success: function (data) {
          $('.snapshot-info').html($(data).find('.snapshot-info').html());
          $('.manager-snapshot').removeClass('active');
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while getting information about snapshots.");
        }
      });
      $(this).dialog('close');
    }
  });

  $('#manager-snapshot-form').dialog({
    autoOpen: false,
    buttons: manager_snapshot_buttons
  });

  $('.manager-snapshot').on('click', function() {
    $(this).addClass('active');
    $('#manger-snapshot-form').dialog('open');
  });


  $('#switch-manager').on('click', function() {
    $.ajax({
      method: 'POST',
      url: '/vsphclient/switchmanager/',
      data: {},
      success: function (data) {
        $('.right-block').html($(data).find('.right-block').html());
      },
      error: function (data) {
        alert("ERROR: Something was going topologywrong while getting information about virtual swithes.");
      }
    });
  });


  // $('#cpu-use').on('click', function() {
  //   $.ajax({
  //     method: 'POST',
  //     url: '/vsphclient/cpuuse/',
  //     data: {},
  //     success: function (data) {
  //       $('.right-block').html($(data).find('.right-block').html());
  //     },
  //     error: function (data) {
  //       alert("ERROR: Something was going wrong while getting information.");
  //     }
  //   });
  // });


  // $('#memory-use').on('click', function() {
  //   $.ajax({
  //     method: 'POST',
  //     url: '/vsphclient/memoryuse/',
  //     data: {},
  //     success: function (data) {
  //       $('.right-block').html($(data).find('.right-block').html());
  //     },
  //     error: function (data) {
  //       alert("ERROR: Something was going wrong while getting information.");
  //     }
  //   });
  // });


  // $('#disk-use').on('click', function() {
  //   $.ajax({
  //     method: 'POST',
  //     url: '/vsphclient/diskuse/',
  //     data: {},
  //     success: function (data) {
  //       $('.right-block').html($(data).find('.right-block').html());
  //     },
  //     error: function (data) {
  //       alert("ERROR: Something was going wrong while getting information.");
  //     }
  //   });
  // });


  // $('#network-use').on('click', function() {
  //   $.ajax({
  //     method: 'POST',
  //     url: '/vsphclient/networkuse/',
  //     data: {},
  //     success: function (data) {
  //       $('.right-block').html($(data).find('.right-block').html());
  //     },
  //     error: function (data) {
  //       alert("ERROR: Something was going wrong while getting information.");
  //     }
  //   });
  // });


  var add_switch_buttons = new Array();
  add_switch_buttons.push({
    text: 'Cancel',
    click: function() {
      $(this).dialog('close');
    }
  });

  add_switch_buttons.push({
    text: 'OK',
    click: function() {
      $(this).removeClass('active');
      $.ajax({
        method: 'POST',
        url: '/vsphclient/addswitch/',
        data: $(this).serialize(),
        success: function (data) {
          $('.operation-history').html($(data).find('.operation-history').html());
          $('.right-block').html($(data).find('.right-block').html());
        },
        error: function (data) {
          alert("ERROR: Something was going wrong while creating virtual switch.");
        }
      });
      $(this).dialog('close');
    }
  });

  $('#add-switch-form').dialog({
    autoOpen: false,
    buttons: add_switch_buttons
  });

  $('.add-switch').on('click', function (){
    console.log("we are here")
    $('#add-switch-form').dialog('open');
  });
});
