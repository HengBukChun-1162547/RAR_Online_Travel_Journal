document.addEventListener('DOMContentLoaded', function() {
    // Get clear button and search input elements
    const clearBtn = document.getElementById('clear_search');
    const searchJourneyContent = document.getElementById('searchJourneyContent');
    const searchJourneyBy = document.getElementById('searchJourneyBy');
    const form = document.getElementById('journeysearch');

    toggleInputState();

    // Add event listener to searchJourneyBy dropdown
    searchJourneyBy.addEventListener('change', toggleInputState);

    function toggleInputState() {
        if (searchJourneyBy.value === '0') {
            searchJourneyContent.disabled = true;
            searchJourneyContent.removeAttribute('required');
            searchJourneyContent.value = '';
        } else {
            searchJourneyContent.disabled = false;
            searchJourneyContent.setAttribute('required', 'required');
        }
    }

    // Add event listener to clear button
    clearBtn.addEventListener('click', function () {
        searchJourneyBy.value = "0"; 
        toggleInputState();
        // Submit the form to show all results
        form.submit();
    })
});