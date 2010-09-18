/*! Javsscript code for Trac Watchlist Plugin 
 * $Id: watchlist.js $
 * */

jQuery(document).ready(function() {
    // Wiki author names
    var osAuthorsHash = new Object();
    var asAuthors = new Array();
    $("table#wikilist tbody td.author").each(function () {
        osAuthorsHash[ $(this).text().replace(/^\s*|\s*$/g,'') ] = 1;
    });
    for (key in osAuthorsHash) {
        asAuthors.push(key);
    }
    if (asAuthors) {
        $("#wikis tfoot th.author input").autocomplete(asAuthors);
    }
    ///

    // Ticket author names
    var osAuthorsHash = new Object();
    var asAuthors = new Array();
    $("table#ticketlist tbody td.author").each(function () {
        osAuthorsHash[ $(this).text().replace(/^\s*|\s*$/g,'') ] = 1;
    });
    for (key in osAuthorsHash) {
        asAuthors.push(key);
    }
    if (asAuthors) {
        $("#tickets tfoot th.author input").autocomplete(asAuthors);
    }
    osAuthorsHash = null;
    asAuthors     = null;
    ///

    // AJAX calls
    var options = {
        delay:750,
        matchCase:true,
        matchSubset:true,
        selectFirst:false,
        multiple:true,
        multipleSeparator:',',
        cacheLength:10,
        max:100,
    }
    // Autocomplete Wiki Names
    $("#wikis .addtowatch input[name=resid]")
        .autocomplete("./watchlist?action=search&realm=wiki", options);
    $("#wikis .remfromwatch input[name=resid],#wikis tfoot th.name input")
        .autocomplete("./watchlist?action=search&realm=wiki&group=watched", options);
    ///
    // Autocomplete Ticket Ids
    $("#tickets .addtowatch input[name=resid]")
        .autocomplete("./watchlist?action=search&realm=ticket", options);
    $("#tickets .remfromwatch input[name=resid]")
        .autocomplete("./watchlist?action=search&realm=ticket&group=watched", options);
    ///
});


