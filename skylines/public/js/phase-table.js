(function() {
  slPhaseTable = function(placeholder) {
    var phase_table = this;

    /**
     * The selected table row or null.
     * @type {?(String|number)}
     */
    var selection = null;

    // Public attributes and functions

    /**
     * @expose
     * Clears the current selection from the table.
     *
     * @param  {Boolean=} opt_trigger
     *   The 'selection_changed' event is triggered if this parameter is true.
     */
    fix_table.clearSelection = function(opt_trigger) {
      fix_table.setSelection(null, opt_trigger);
    };

    /**
     * @expose
     * Selects a new flight phase from the table.
     *
     * @param {?Object} element The table row that should be selected.
     * @param  {Boolean=} opt_trigger
     *   The 'selection_changed' event is triggered if this parameter is true.
     */
    phase_table.setSelection = function(element, opt_trigger) {
      if (selection)
        $(selection).removeClass('selected');

      selection = element;

      if (selection)
        $(selection).addClass('selected');

      if (opt_trigger) {
        if (selection) {
          var start = parseFloat(
              $(selection).children('td.start').attr('data-content'));
          var duration = parseFloat(
              $(selection).children('td.duration').attr('data-content'));

          $(phase_table).trigger('selection_changed', [{
            start: start,
            end: start + duration,
            duration: duration
          }]);
        } else {
          $(phase_table).trigger('selection_changed');
        }
      }
    };

    // Initialization

    changePointer();
    setupEvents();

    function changePointer() {
      placeholder.find('tr').each(function(index, row) {
        $(row).css('cursor', 'pointer');
      });
    }

    function setupEvents() {
      placeholder.on('click', 'tr', function(event) {
        phase_table.setSelection(selection == this ? null : this, true);
      });
    }
  };
})();
