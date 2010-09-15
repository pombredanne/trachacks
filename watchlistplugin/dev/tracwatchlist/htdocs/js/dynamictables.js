/*! Javsscript code for Trac Watchlist Plugin 
 * $Id: watchlist.js $
 * */

function wldeleterow(tr, table) {
  $(table).dataTable().fnDeleteRow(tr);
}

// Cookie Code taken from http://www.quirksmode.org/js/cookies.html
// 15th Sep 2010
// Changes: added path argument
function createCookie(name,value,days,path) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    if ( !path ) {
        path = "/";
    }
    document.cookie = name+"="+value+expires+"; path=" + path;
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ')
            c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0)
            return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name,"",-1);
}
/// End of Cookie Code


// Store datetime filter inputs on unload
jQuery(window).unload(function() {
    $(".datetimefilter").each(function(){
        dtid = $(this).attr('id');
        $(this).find("input").each(function(){
            var name = dtid + '/' + $(this).attr('name');
            var value = $(this).val();
            if ($(this).is("input[type=checkbox]")) {
                value = $(this).is(":checked") ? 'checked' : '';
            }
            createCookie(name,value,90,window.location.pathname);
        });
    });
});

// Restore datetime filter inputs on load
jQuery(document).ready(function() {
    $(".datetimefilter").each(function(){
        dtid = $(this).attr('id');
        $(this).find("input").each(function(){
            var name = dtid + '/' + $(this).attr('name');
            var value = readCookie(name);
            if ($(this).is("input[type=checkbox]")) {
                $(this).attr('checked', value =='checked' );
                $(this).change();
            }
            else {
                $(this).val(value);
                $(this).keyup();
            }
        });
    });
});

$.fn.dataTableExt.afnFiltering.push(
    function( oSettings, aData, iDataIndex ) {
        var table = $('#'+ oSettings.sTableId);
        var checked = $(table).find('input[name=sincelastvisit]').is(':checked');
        if ( !checked ) {
            return true;
        }

        var iColumn = 1;
        var n = document.createElement('div');
        n.innerHTML = aData[iColumn];
        timestamp = $(n).find('span.itime').text();
        if ( !timestamp ) {
            return true;
        }
        lastvisit = $('#last_visit').val();
        if ( timestamp < lastvisit ) {
            return false;
        }

        return true;


        var iMin = $(table).find('input[name=from-datetime]').val();
        var iMax = $(table).find('input[name=to-datetime]').val();
        alert( "iMin = " + iMin + ", iMax = " + iMax )
        if ( !iMin && !iMax ) {
            return true;
        }
        return false;
        var iColumn = 1;
        var iMin = document.getElementById('min').value * 1;
        var iMax = document.getElementById('max').value * 1;
        
        var iVersion = aData[iColumn] == "-" ? 0 : aData[iColumn]*1;
        if (0) { }
        else if ( iMin == "" && iVersion < iMax )
        {
            return true;
        }
        else if ( iMin < iVersion && "" == iMax )
        {
            return true;
        }
        else if ( iMin < iVersion && iVersion < iMax )
        {
            return true;
        }
        return false;
    }
);



jQuery(document).ready(function() {
  // Dynamic Table
  $("table.watchlist").each(function(){
    // Disabled sorting of marked columns (unwatch, notify, etc.)
    var aoColumns = [];
    $(this).find('thead th').each( function () {
      if ( $(this).hasClass( 'sorting_disabled' ) ) {
        aoColumns.push( { "bSortable": false, "bSearchable": false } );
      } else {
        aoColumns.push( null );
      }
    });
    /* // Fixed width for name column (nonfunctional)
    if (aoColumns[0] == null) {
      aoColumns[0] = {};
    }
    aoColumns[0]['sWidth'] = $(this).find('thead th.name').css('width');
    */
    // Activate dataTable
    $(this).dataTable({
    "bStateSave": true,
    "aoColumns": aoColumns,
    //"bAutoWidth": false,
    //"bJQueryUI": true,
    "sPaginationType": "full_numbers",
    "bPaginate": true,
    "sDom": 'ilpfrt',
    "sPagePrevious": "&lt;",
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "&#8734;"]],
    //"sPaginationType": "full_numbers",
    // Remove empty table
    "fnHeaderCallback": function ( nRow, aaData, iStart, iEnd, aiDisplay ) {
         if (aaData.length == 0) {
            wlremoveempty( nRow );
         }
    },
    "oLanguage": {
      "sLengthMenu": "_MENU_",
      "sZeroRecords": "./.",
      "sInfo": "_START_-_END_ / _TOTAL_",
      "sInfoEmpty": "./.",
      "sInfoFiltered": "(_MAX_)",
      "sProcessing": "...",
      "sInfoPostFix": "",
      "sSearch": "",
      "sUrl": "",
      "oPaginate": {
        "sFirst":    "|&lt;",
        "sPrevious": "&lt;",
        "sNext":     "&gt;",
        "sLast":     "&gt;|"
      },
      "fnInfoCallback": null
    },
   });
  });


  /* Per-column filters */
  $("table.watchlist").each( function () {
    var table  = this;
    var oTable = $(this).dataTable();

    /* Per-column filter input fields in footer */
    $(this).find("tfoot input.filter").keyup( function () {
      var index = $(table).find("tfoot th").index( $(this).parent("th") );
      oTable.fnFilter( this.value, index );
    });

    /* Restore per-column input values after page reload */
    var oSettings = oTable.fnSettings();
    $(this).find("tfoot th").each( function (i) {
      $(this).find("input.filter").val( oSettings.aoPreSearchCols[i].sSearch );
    });

    $(this).find("input[name=sincelastvisit]").change( function () {
      oTable.fnDraw();
    });
  });
});

/* Remove column sorting input when preferences are updated.
 * This is because the column order could have changed.
 * */
function wlprefsubmit(force){
  $("fieldset.orderadd").each( function () {
    if (force || $(this).data('modified')) {
      realm = $(this).data('realm');
      table = $("table#" + realm + "list");
      var oTable = $(table).dataTable();
      a = $(table).find("tfoot th");
      $(table).find("tfoot th").each( function (i) {
          oTable.fnFilter("",i);
      });
    }
  });
}



