// Event Detail Page JavaScript
// Handles event-specific premium features and photo management

document.addEventListener('DOMContentLoaded', function() {
    
    // Clear validation when modal is closed
    const staffPhotoRemovalModal = document.getElementById('staffPhotoRemovalModal');
    if (staffPhotoRemovalModal) {
        staffPhotoRemovalModal.addEventListener('hidden.bs.modal', function() {
            const form = document.getElementById('staffPhotoRemovalForm');
            const reasonField = document.getElementById('staff_photo_removal_reason');
            
            if (form) form.reset();
            if (reasonField) reasonField.classList.remove('is-invalid');
        });
    }

    // Handle "Maybe Later" button click for add multiple images modal
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'premiumLaterBtn') {
            const modal = e.target.closest('.modal');
            if (modal && modal.id === 'addmultipleImagesModal') {
                const permissions = document.getElementById('permissions');
                const eventId = permissions.dataset.eventId;
                window.location.href = `/event/photo/${eventId}`;
            }
        }
    });
});

// Check permission for adding multiple images
function showPremium2Modal(featureName, event) {
    const permissions = document.getElementById('permissions');
    const hasEventimagesPermission = JSON.parse(permissions.dataset.hasEventimagesPermission);

    if (!hasEventimagesPermission) {
        event.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('addmultipleImagesModal'));
        modal.show();
        return false;
    }
    return true;
}

// Check permission for following location
function showPremiumModal(featureName, event) {
    const permissions = document.getElementById('permissions');
    const hasFollowlocationPermission = JSON.parse(permissions.dataset.hasFollowlocationPermission);

    if (!hasFollowlocationPermission) {
        event.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('followLocationModal'));
        modal.show();
        return false;
    }

    return true;
}

// Handle photo removal with staff reason requirement
function handlePhotoRemoval(imagePath, submitEvent) {
    const permissions = document.getElementById('permissions');
    const hasEditotherspubliceventPermission = JSON.parse(permissions.dataset.hasEditotherspubliceventPermission);
    const hasisstaffPermission = JSON.parse(permissions.dataset.isstaffPermission);
    
    if (hasisstaffPermission && hasEditotherspubliceventPermission) {
        // Prevent default form submission
        if (submitEvent) {
            submitEvent.preventDefault();
        }
        
        // Set the image path in the modal form
        const staffImagePathInput = document.getElementById('staff_image_path_to_delete');
        if (staffImagePathInput) {
            staffImagePathInput.value = imagePath;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('staffPhotoRemovalModal'));
        modal.show();
        
        return false;
    } else {
        // Regular user - proceed with normal confirmation
        return confirm('Are you sure you want to delete this photo?');
    }
}
