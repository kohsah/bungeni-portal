(function($) {
  $(document).ready(function() {
      // prepare alchemist content views
      var manager = $(".alchemist-content-manager");
      manager.yuiTabView(manager.find("div.listing"));

      // wire workflow dropdown menu to use POST actions
      var menu_links = $('#plone-contentmenu-workflow dd.actionMenuContent a');
      menu_links.bungeniPostWorkflowActionMenuItem();

      // set up time range form automation
      $("select").bungeniTimeRangeSelect();

      // set up 
    });
 })(jQuery);
