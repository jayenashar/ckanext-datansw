document.addEventListener("DOMContentLoaded", function(event) { 
  caBoootstrap.init("https://feedbackassist.onegov.nsw.gov.au/feedbackassist");
});

jQuery(document).ready(function() {
  caBoootstrap.init("https://feedbackassist.onegov.nsw.gov.au/feedbackassist");
});

datansw_updateToTopButton();
jQuery(document)
  .on('scroll', datansw_updateToTopButton)
  .find('.to-top')
  .on('click', datansw_smoothScrollToTop);
jQuery(document)
  .find('.page-tile')
  .parents('ul')
  .addClass('tile-list');


function datansw_updateToTopButton() {
  jQuery('.to-top')[
    jQuery(document).scrollTop() > 150 ? 'addClass' : 'removeClass'
  ]('show');
}

function datansw_smoothScrollToTop() {
  jQuery('body,html').animate({ scrollTop: 0 }, 400);
}