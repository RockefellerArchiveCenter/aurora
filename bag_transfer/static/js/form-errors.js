/**
 * Moves focus to form errors after a page load.
 *
 * 1. If error summary is present (`.form-error-summary`), focus moves there.
 * 2. If any input has an inline error (`aria-invalid="true"`), focus moves to the first invalid input.
 * 3. For fieldset elements that aren't focusable by default, focus moves to the first input.
 *
 */
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    var summary = document.querySelector('.form-error-summary');
    if (summary) {
      summary.focus();
      return;
    }

    var firstInvalidField = document.querySelector('[aria-invalid="true"]');
    if (!firstInvalidField) {
      return;
    }

    if (firstInvalidField.tagName === 'FIELDSET') {
      var firstInput = firstInvalidField.querySelector('input, select, textarea');
      if (firstInput) {
        firstInput.focus();
      }
    } else {
      firstInvalidField.focus();
    }
  }, 100); //delay in ms to let browser finish constructing the accessibility tree before moving focus
});
