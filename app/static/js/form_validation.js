document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    (() => {
        'use strict'
      
        // Get all forms requiring validation
        const forms = document.querySelectorAll('.needs-validation')
      
        // Add validation to each form
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
          
                form.classList.add('was-validated')
            }, false)
        })
    })()
});