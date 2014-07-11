function getFormData(formId) {
    //create requestObj from search form
    var searchForm = $(formId).find(':input').not($('button'));
    var formData = {};
    $.each(searchForm, function (formData) {
        return function (index, inputItem) {
            if ($(inputItem).attr('type') == 'checkbox') {
                if ($(inputItem).is(':checked')) {
                    formData[$(inputItem).attr('name')] = $(inputItem).val();
                }
            }
            else {
                formData[$(inputItem).attr('name')] = $(inputItem).val();
            }
        }
    }(formData));

    return formData;
}

function chooseSlideDirection(targetId) {
    var Elem = $(targetId);
    if ($(Elem).css("display") == "none") { Elem.slideDown(); }
    else { Elem.slideUp(); }
}


$(document).ready(function () {
    $('#about').click(function() {
        chooseSlideDirection('#aboutTarget');
        $('#helpTarget').slideUp();
        $('#creditsTarget').slideUp();
    });
    $('#help').click(function() {
        chooseSlideDirection('#helpTarget');
        $('#aboutTarget').slideUp();
        $('#creditsTarget').slideUp();
    });
    $('#credits').click(function() {
        chooseSlideDirection('#creditsTarget');
        $('#helpTarget').slideUp();
        $('#aboutTarget').slideUp();
    });
    
    $("#acceptterms").click(function () {
        $(this).css({
            background: "",
            border: ""
        });
    });

    $('#search-reset').click(function () {
        $('#search')[0].reset();
        $('#resultsPanel').html('');
    });

    $('#search-list, #search-full, #search-grid').click(function () {
        submitForm($(this).attr('name'));
    });

    $('#search input[type=text]').keypress(function(event) {
        if (event.which == 13) {
            submitForm('search-list');
        }
    });

    $('[name]').map(function () {
        var elementID = $(this).attr('name');
        if (elementID.indexOf('.') == 2) {
            // console.log(elementID);
            $(this).autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "../../autosuggest/?",
                        dataType: "json",
                        data: {
                            q: request.term,
                            elementID: elementID
                        },
                        success: function (data) {
                            response(data);
                        }
                    });
                },
                minLength: 2,
            });
        }
    });

    var submitForm = function(displaytype) {
        var formData = getFormData('#search');
        formData[displaytype] = '';

        if (!formData['acceptterms']) {
            $("#acceptterms")
                .css({
                    background: "yellow",
                    border: "3px red solid"
                });
        }
        else {
            $('#resultsPanel').css({
                display: "none"
            });

            $('#waitingImage').css({
                display: "block"
            });

            $.post("../results/", formData).done(function (data) {
                $('#resultsPanel').html(data);
                $('#resultsListing').tablesorter({
                    headers: {
                        0: {sorter: false},
                        1: {width: '100px' },
                        2: {width: '260px' },
                        4: {width: '90px', sorter: 'isoDate' },
                        9: {width: '180px' }
                    }
                });
                $('#tabs').tabs({ active: 0 });
                ga('send', 'pageview', { 'page': '/search' });

                $('#resultsPanel').css({
                    display: "block"
                });

                $('#waitingImage').css({
                    display: "none"
                });
            });
        }
    };

    $(document).on('click', '#select-items', function() {
        if ($('#select-items').is(':checked')) {
            $('#selectedItems input:checkbox').prop('checked', true);
        } else {
            $('#selectedItems input:checkbox').prop('checked', false);
        }
    });

    $(document).on('click', '.map-item', function () {
        var Elem = $(this).siblings('.small-map');
        if ($(Elem).css("display") == "none") {
            var marker = ($(Elem).attr('data-marker'));
            console.log('img ' + marker);
            $(Elem).html('<img src="http://maps.google.com/maps/api/staticmap?&zoom=10&size=400x200&maptype=roadmap&markers=' +
            marker + '&sensor=false"/>' +
            '<div style="height: 40px;">' +
            '<small><a target="_map" href="https://maps.google.com/maps/i?q=loc:'+marker+'&amp;source=embed">Larger Map</a>'+
            '</small></div>');
            Elem.slideDown();
            ga('send', 'pageview', { 'page': '/map/inline' });
        }
        else {
            Elem.slideUp();
        }
    });

    $(document).on('click', '.facet-item', function () {
        var key = ($(this).attr('data-facetType'));
        var value = ($(this).text());

        if (key != '') {
            var keyElement = $('#' + key);
            var keyElQual = $('#' + key + '_qualifier');
            if (keyElement != null) {
                keyElement.val(value);
                if (keyElQual != null) {
                    keyElQual.val('exact');
                }
            }
        }

        var formData = getFormData('#search');
        // TODO: CURRENTLY DEFAULT TO SEARCH-LIST BUT SHOULD HAVE A PERSISTENT DISPLAY TYPE? CURRENTLY DOESN'T ON DEV
        formData['search-list'] = '';

        $.post("../results/", formData).done(function (data) {
            $('#resultsPanel').html(data);
            $('#resultsListing').tablesorter({
                headers: {
                    0: {sorter: false},
                    1: {width: '100px' },
                    2: {width: '260px' },
                    4: {width: '90px', sorter: 'isoDate' },
                    9: {width: '180px' }
                }
            });
            $('#tabs').tabs({ active: 1 });
            ga('send', 'pageview', { 'page': '/search/refine' });
        });
    });

    $(document).on('click', '#map-bmapper, #map-google', function () {
        var formData = getFormData('#selectedItems');
        // formData[$(this).attr('name')] = '';

        if ($(this).attr('id') == 'map-bmapper') {
            $.post("../bmapper/", formData).done(function (data) {
                window.open(data, '_blank');
            });
            ga('send', 'pageview', { 'page': '/map/bmapper' });
        } else if ($(this).attr('id') == 'map-google') {
            $.post("../gmapper/", formData).done(function (data) {
                $('#maps').html(data);
            });
            ga('send', 'pageview', { 'page': '/map/google' });
        }
    });
// we need to make sure this gets done in the event the page is created anew (e.g. via a pasted URL)
$('#tabs').tabs({ active: 0 });
});