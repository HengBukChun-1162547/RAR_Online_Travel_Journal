// Journey Detail Page JavaScript
// Handles edit mode, cover image management, and premium feature checks

document.addEventListener('DOMContentLoaded', function() {
    // Track if any changes have been made that require staff reason
    let requiresStaffReason = false;

    // Track the previously selected radio button
    let previouslySelectedRadio = null;

    // Initialize character counters
    initializeCharacterCounters();

    // Handle published radio button change
    function handlePublishedRadioChange() {
        const permissions = document.getElementById('permissions');
        const hasPublishPermission = JSON.parse(permissions.dataset.hasPublishPermission);

        if (this.checked && !hasPublishPermission) {
            // User doesn't have publish permission, show modal and revert selection
            this.checked = false;

            // Revert to the previously selected radio button
            if (previouslySelectedRadio && previouslySelectedRadio !== this) {
                previouslySelectedRadio.checked = true;
            } else {
                // Fallback: check which radio was selected before this change
                const privateRadio = document.getElementById('private');
                const publicRadio = document.getElementById('public');

                // Default to private if no previous selection found
                privateRadio.checked = true;
            }

            // Show publish journey modal
            const publishJourneyModal = new bootstrap.Modal(document.getElementById('publishJourneyModal'));
            publishJourneyModal.show();
        }
    }

    // Track radio button changes to remember the previous selection
    function trackRadioSelection() {
        const radios = document.querySelectorAll('input[name="sharing"]');
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked && this.id !== 'published') {
                    // Remember this selection for potential revert
                    previouslySelectedRadio = this;
                }
            });
        });
    }

    // Toggle edit mode
    window.toggleEdit = function() {
        const form = document.getElementById('journeyForm');
        const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea');
        const radios = form.querySelectorAll('input[type="radio"]');
        const checkboxes = form.querySelectorAll('input[type="checkbox"]:not(#remove_cover)');
        const fileInput = document.getElementById('cover_image');
        const removeCheck = document.getElementById('remove_cover');
        const editButton = document.getElementById('editButton');
        const editButtons = document.getElementById('editButtons');
        const staffReasonSection = document.getElementById('staffReasonSection');

        // Get permissions from data attributes
        const permissions = document.getElementById('permissions');
        const hasPublishPermission = JSON.parse(permissions.dataset.hasPublishPermission);
        const isStaff = JSON.parse(permissions.dataset.isStaff);
        const isJourneyOwner = JSON.parse(permissions.dataset.isJourneyOwner);
        const user_status = permissions.dataset.userStatus;

        // Show staff reason section if staff is editing others' journey
        if (isStaff && !isJourneyOwner && staffReasonSection) {
            staffReasonSection.style.display = 'block';
        }

        // Enable file input
        if (fileInput) {
            fileInput.disabled = !fileInput.disabled;
        }

        // Enable remove cover checkbox
        if (removeCheck) {
            removeCheck.disabled = false;
            console.log('remove_cover disabled state:', removeCheck.disabled);
        }

        // Toggle readonly/disabled state
        inputs.forEach(input => {
            if (input.id === 'staff_reason') {
            // Don't change staff reason field
                return;
            } else if (input.id === 'start_date' && isStaff && !isJourneyOwner) {
                input.readOnly = true;
            } else {
                // Toggle readonly for all other inputs
                input.readOnly = !input.readOnly;
            }

            // Add change listeners to track modifications for staff
            if (isStaff && !isJourneyOwner && (input.id === 'title' || input.id === 'description')) {
                input.addEventListener('input', function() {
                    requiresStaffReason = true;
                    markFieldAsRequired();
                });
            }
        });

        radios.forEach(radio => {
            // For staff users editing others' journeys, don't enable sharing status radios
            if (isStaff && !isJourneyOwner) {
                // Staff cannot modify sharing status of others' journeys
                return;
            }
            // For journey owners, enable all radio buttons including Published
            if (user_status === 'restricted') {
                // Disable Published and Public for restricted users
                if (radio.id === 'published' || radio.id === 'public') {
                    radio.disabled = true;
                }
                else{
                    radio.disabled = false;
                }
            }
            else {
                // Enable all radio buttons for non-restricted users
                radio.disabled = false;
            }
        });

        // Initialize radio button tracking and set initial previous selection
        setTimeout(function() {
            // Set the initially selected radio as the previous selection
            const currentlySelected = document.querySelector('input[name="sharing"]:checked');
            if (currentlySelected && currentlySelected.id !== 'published') {
                previouslySelectedRadio = currentlySelected;
            }

            // Start tracking radio button changes
            trackRadioSelection();

            // Add event listener for published radio button to check permissions
            const publishedRadio = document.getElementById('published');
            if (publishedRadio && !publishedRadio.disabled) {
                // Remove any existing event listeners to avoid duplicates
                publishedRadio.removeEventListener('change', handlePublishedRadioChange);
                // Add the event listener
                publishedRadio.addEventListener('change', handlePublishedRadioChange);
            }
        }, 0);

        // Toggle checkboxes (like no_edits)
        checkboxes.forEach(checkbox => {
            checkbox.disabled = !checkbox.disabled;
        });

        // Toggle cover image UI
        const coverAddOverlay = document.getElementById('coverAddOverlay');
        const changeCoverOverlay = document.getElementById('changeCoverOverlay');
        const deleteCoverBtn = document.getElementById('deleteCoverBtn');
        const currentCoverImage = document.getElementById('currentCoverImage');
        const removeCoverInput = document.getElementById('remove_cover');
        const hasCurrentImage = document.getElementById('coverImageDisplay') !== null;
        const isMarkedForRemoval = removeCoverInput && removeCoverInput.value === '1';

        if (coverAddOverlay) {
            // Show Add button only if no current image or image is marked for removal
            if (!hasCurrentImage || isMarkedForRemoval) {
                coverAddOverlay.classList.toggle('d-none');
            }
        }

        if (changeCoverOverlay) {
            // Show Change button only if there's a current image and it's not marked for removal
            if (hasCurrentImage && !isMarkedForRemoval) {
                changeCoverOverlay.classList.toggle('d-none');
            }
        }

        if (deleteCoverBtn && hasCurrentImage && !isMarkedForRemoval) {
            // Show delete button only if there's an image, user can delete, and it's not already marked for removal
            const canDeleteCover = permissions.dataset.canDeleteCover === 'true';
            if (canDeleteCover) {
                deleteCoverBtn.classList.toggle('d-none');
            }
        }

        // Toggle buttons visibility
        editButton.classList.toggle('d-none');
        editButtons.classList.toggle('d-none');

        // Reset validation state
        form.classList.remove('was-validated');
    };

    // Mark staff reason field as required
    function markFieldAsRequired() {
        const staffReasonField = document.getElementById('staff_reason');
        if (staffReasonField) {
            staffReasonField.required = true;
            staffReasonField.classList.add('border-danger');
        }
    }

    // Validate staff reason before form submission
    window.validateStaffReason = function() {
        const permissions = document.getElementById('permissions');
        const isStaff = JSON.parse(permissions.dataset.isStaff);
        const isJourneyOwner = JSON.parse(permissions.dataset.isJourneyOwner);

        if (isStaff && !isJourneyOwner && requiresStaffReason) {
            const staffReasonField = document.getElementById('staff_reason');
            const staffReasonValue = staffReasonField.value.trim();

            if (!staffReasonValue) {
                staffReasonField.classList.add('is-invalid');
                staffReasonField.focus();

                // Show alert
                alert('Please provide a reason for modifying this user\'s journey.');
                return false;
            }

            staffReasonField.classList.remove('is-invalid');
        }

        return true;
    };

    // Cancel edit
    window.cancelEdit = function() {
        const form = document.getElementById('journeyForm');
        const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea');
        const radios = form.querySelectorAll('input[type="radio"]');
        const checkboxes = form.querySelectorAll('input[type="checkbox"]:not(#remove_cover)');
        const fileInput = document.getElementById('cover_image');
        const removeCheck = document.getElementById('remove_cover');
        const editButton = document.getElementById('editButton');
        const editButtons = document.getElementById('editButtons');
        const staffReasonSection = document.getElementById('staffReasonSection');

        // Hide staff reason section
        if (staffReasonSection) {
            staffReasonSection.style.display = 'none';
        }

        // Reset staff reason tracking
        requiresStaffReason = false;

        // Reset form values
        form.reset();

        // Make inputs readonly again
        inputs.forEach(input => {
            if (input.id !== 'staff_reason') {
                input.readOnly = true;
            }
            input.classList.remove('is-invalid', 'border-danger');
        });

        radios.forEach(radio => {
            radio.disabled = true;
        });

        // Disable checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.disabled = true;
        });

        if (removeCheck) {
            removeCheck.disabled = false;
            removeCheck.value = '0'; // reset to 0
            console.log('remove_cover reset to:', removeCheck.value, 'disabled:', removeCheck.disabled);
        }

        // Reset cover image UI
        resetCoverImageUI();

        // Hide cover image controls
        const coverAddOverlay = document.getElementById('coverAddOverlay');
        const changeCoverOverlay = document.getElementById('changeCoverOverlay');
        const deleteCoverBtn = document.getElementById('deleteCoverBtn');

        if (coverAddOverlay) {
            coverAddOverlay.classList.add('d-none');
        }

        if (changeCoverOverlay) {
            changeCoverOverlay.classList.add('d-none');
        }

        if (deleteCoverBtn) {
            deleteCoverBtn.classList.add('d-none');
        }

        // Clear file input
        if (fileInput) {
            fileInput.value = '';
            fileInput.disabled = true;
        }

        // Reset buttons visibility
        editButton.classList.remove('d-none');
        editButtons.classList.add('d-none');

        // Reset validation state
        form.classList.remove('was-validated');
    };

    // Show delete confirmation modal
    window.confirmDelete = function() {
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
        deleteModal.show();
    };

    // Trigger cover image upload
    window.triggerCoverUpload = function() {
        const permissions = document.getElementById('permissions');
        const hasCoverPermission = JSON.parse(permissions.dataset.hasCoverPermission);

        if (!hasCoverPermission) {
            const premiumModal = new bootstrap.Modal(document.getElementById('coverImageModal'));
            premiumModal.show();
            return false;
        }

        const fileInput = document.getElementById('cover_image');
        if (fileInput) {
            fileInput.disabled = false;
            fileInput.click();
        }
    };

    // Trigger cover image change (for existing cover images)
    window.triggerCoverChange = function() {
        const permissions = document.getElementById('permissions');
        const hasCoverPermission = JSON.parse(permissions.dataset.hasCoverPermission);

        if (!hasCoverPermission) {
            const premiumModal = new bootstrap.Modal(document.getElementById('coverImageModal'));
            premiumModal.show();
            return false;
        }

        const fileInput = document.getElementById('cover_image');
        if (fileInput) {
            fileInput.disabled = false;
            fileInput.click();
        }
    };

    // Handle cover image change
    window.handleCoverImageChange = function(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];

            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file format. Please upload an image file (PNG, JPG, JPEG, GIF).');
                input.value = '';
                return;
            }

            // Validate file size (5MB)
            const maxSize = 5 * 1024 * 1024; // 5MB in bytes
            if (file.size > maxSize) {
                alert('File size exceeds the 5MB limit. Please choose a smaller image file.');
                input.value = '';
                return;
            }

            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                showCoverImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);

            // Track staff changes
            const permissions = document.getElementById('permissions');
            const isStaff = JSON.parse(permissions.dataset.isStaff);
            const isJourneyOwner = JSON.parse(permissions.dataset.isJourneyOwner);

            if (isStaff && !isJourneyOwner) {
                requiresStaffReason = true;
                markFieldAsRequired();
            }
        }
    };

    // Show cover image preview
    function showCoverImagePreview(imageSrc) {
        const currentCoverImage = document.getElementById('currentCoverImage');
        const previewCoverImage = document.getElementById('previewCoverImage');
        const coverImagePreview = document.getElementById('coverImagePreview');
        const coverAddOverlay = document.getElementById('coverAddOverlay');
        const changeCoverOverlay = document.getElementById('changeCoverOverlay');
        const deleteCoverBtn = document.getElementById('deleteCoverBtn');

        // Hide current image and overlays
        if (currentCoverImage) {
            currentCoverImage.classList.add('d-none');
        }

        if (coverAddOverlay) {
            coverAddOverlay.classList.add('d-none');
        }

        if (changeCoverOverlay) {
            changeCoverOverlay.classList.add('d-none');
        }

        // Show preview image
        if (previewCoverImage && coverImagePreview) {
            coverImagePreview.src = imageSrc;
            previewCoverImage.classList.remove('d-none');
        }

        // Show delete button for preview
        if (deleteCoverBtn) {
            deleteCoverBtn.classList.remove('d-none');
        }
    }

    // Reset cover image UI
    function resetCoverImageUI() {
        const currentCoverImage = document.getElementById('currentCoverImage');
        const previewCoverImage = document.getElementById('previewCoverImage');
        const coverImagePreview = document.getElementById('coverImagePreview');
        const removeCoverInput = document.getElementById('remove_cover');
        const deleteCoverBtn = document.getElementById('deleteCoverBtn');
        const coverAddOverlay = document.getElementById('coverAddOverlay');
        const changeCoverOverlay = document.getElementById('changeCoverOverlay');

        // Show current image
        if (currentCoverImage) {
            currentCoverImage.classList.remove('d-none');
        }

        // Hide preview image
        if (previewCoverImage) {
            previewCoverImage.classList.add('d-none');
        }

        // Clear preview src
        if (coverImagePreview) {
            coverImagePreview.src = '';
        }

        // Reset remove cover flag
        if (removeCoverInput) {
            removeCoverInput.value = '0';
        }

        // Reset delete button state based on whether there's a current image
        const hasCurrentImage = document.getElementById('coverImageDisplay') !== null;
        const permissions = document.getElementById('permissions');
        const canDeleteCover = permissions.dataset.canDeleteCover === 'true';
        
        if (deleteCoverBtn) {
            if (hasCurrentImage && canDeleteCover) {
                // Only show delete button if there's actually an image to delete
                deleteCoverBtn.classList.add('d-none'); // Keep hidden initially, will be shown in edit mode
            } else {
                deleteCoverBtn.classList.add('d-none');
            }
        }

        // Reset overlay states
        if (coverAddOverlay) {
            if (!hasCurrentImage) {
                coverAddOverlay.classList.add('d-none'); // Will be shown in edit mode if needed
            } else {
                coverAddOverlay.classList.add('d-none');
            }
        }

        if (changeCoverOverlay) {
            if (hasCurrentImage) {
                changeCoverOverlay.classList.add('d-none'); // Will be shown in edit mode if needed
            } else {
                changeCoverOverlay.classList.add('d-none');
            }
        }
    }

    // Remove cover image
    window.removeCoverImage = function() {
        const removeCoverInput = document.getElementById('remove_cover');
        const currentCoverImage = document.getElementById('currentCoverImage');
        const previewCoverImage = document.getElementById('previewCoverImage');
        const deleteCoverBtn = document.getElementById('deleteCoverBtn');
        const coverAddOverlay = document.getElementById('coverAddOverlay');
        const changeCoverOverlay = document.getElementById('changeCoverOverlay');
        const fileInput = document.getElementById('cover_image');

        removeCoverInput.disabled = false;
        // Set remove flag
        if (removeCoverInput) {
            removeCoverInput.value = '1';
        }
        console.log('Cover image marked for removal: ' + (removeCoverInput ? removeCoverInput.value : 'null'));
        // Clear file input completely
        if (fileInput) {
            fileInput.value = '';
            // Force clear the file input by recreating it
            const newFileInput = document.createElement('input');
            newFileInput.type = 'file';
            newFileInput.id = 'cover_image';
            newFileInput.name = 'cover_image';
            newFileInput.setAttribute('form', 'journeyForm');
            newFileInput.accept = 'image/*';
            newFileInput.style.display = 'none';
            newFileInput.onchange = function() { handleCoverImageChange(this); };
            
            // Replace the old input with the new one
            fileInput.parentNode.replaceChild(newFileInput, fileInput);
        }

        // Hide current and preview images
        if (currentCoverImage) {
            currentCoverImage.classList.add('d-none');
        }

        if (previewCoverImage) {
            previewCoverImage.classList.add('d-none');
        }

        // Hide delete button and change overlay immediately after confirmation
        if (deleteCoverBtn) {
            deleteCoverBtn.classList.add('d-none');
        }

        if (changeCoverOverlay) {
            changeCoverOverlay.classList.add('d-none');
        }

        // Show add overlay
        if (coverAddOverlay) {
            coverAddOverlay.classList.remove('d-none');
        }

        // Track staff changes
        const permissions = document.getElementById('permissions');
        const isStaff = JSON.parse(permissions.dataset.isStaff);
        const isJourneyOwner = JSON.parse(permissions.dataset.isJourneyOwner);

        if (isStaff && !isJourneyOwner) {
            requiresStaffReason = true;
            markFieldAsRequired();
        }
    };

    // Handle remove cover checkbox change
    window.handleRemoveCoverChange = function() {
        const permissions = document.getElementById('permissions');
        const isStaff = JSON.parse(permissions.dataset.isStaff);
        const isJourneyOwner = JSON.parse(permissions.dataset.isJourneyOwner);

        if (isStaff && !isJourneyOwner) {
            requiresStaffReason = true;
            markFieldAsRequired();
        }
    };

    // Initialize character counters for title and description
    function initializeCharacterCounters() {
        const titleInput = document.getElementById('title');
        const descriptionInput = document.getElementById('description');
        const titleCharCount = document.getElementById('titleCharCount');
        const descriptionCharCount = document.getElementById('descriptionCharCount');

        // Update character count function to match helpdesk style
        function updateCharacterCount(input, countElement, maxLength) {
            const currentLength = input.value.length;
            countElement.textContent = currentLength + '/' + maxLength;
            
            // Use the same color logic as helpdesk_create.html
            if (maxLength === 50) {
                countElement.className = currentLength > 40 ? 'text-warning' : currentLength > 45 ? 'text-danger' : 'text-muted';
            } else if (maxLength === 300) {
                countElement.className = currentLength > 250 ? 'text-warning' : currentLength > 280 ? 'text-danger' : 'text-muted';
            } else {
                countElement.className = 'text-muted';
            }
        }

        // Add event listeners for real-time updates
        if (titleInput && titleCharCount) {
            titleInput.addEventListener('input', function() {
                updateCharacterCount(this, titleCharCount, 50);
            });
        }

        if (descriptionInput && descriptionCharCount) {
            descriptionInput.addEventListener('input', function() {
                updateCharacterCount(this, descriptionCharCount, 300);
            });
        }
    }

    // Expose resetCoverImageUI to global scope for use in cancelEdit
    window.resetCoverImageUI = resetCoverImageUI;
});