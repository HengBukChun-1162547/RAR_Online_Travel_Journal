document.addEventListener('DOMContentLoaded', function() {

    function checkDepartureboardPermission(event) {
        const permissions = document.getElementById('permissions');
        const hasDepartureboardPermission = JSON.parse(permissions.dataset.hasDepartureboardPermission);

        if (!hasDepartureboardPermission) {
            event.preventDefault();
            const followJourneyModal = new bootstrap.Modal(document.getElementById('departureBoardModal'));
            followJourneyModal.show();
            return false;
        }

        return true;
    }

    const departureBoardLinks = document.querySelectorAll('a[href*="departure_board"]');
    departureBoardLinks.forEach(link => {
        link.addEventListener('click', checkDepartureboardPermission);
    });
});

// Global functions for follow permissions (used across multiple pages)
function checkFollowPermission(event) {
    const permissions = document.getElementById('permissions');
    const hasFollowPermission = JSON.parse(permissions.dataset.hasFollowuserPermission);

    if (!hasFollowPermission) {
        event.preventDefault();
        const followModal = new bootstrap.Modal(document.getElementById('followUserModal'));
        followModal.show();
        return false;
    }

    return true;
}

function checkFollowJourneyPermission(event) {
    const permissions = document.getElementById('permissions');
    const hasFollowJourneyPermission = JSON.parse(permissions.dataset.hasFollowjourneyPermission);

    if (!hasFollowJourneyPermission) {
        event.preventDefault();
        const followJourneyModal = new bootstrap.Modal(document.getElementById('followJourneyModal'));
        followJourneyModal.show();
        return false;
    }

    return true;
}

function showFollowUserPremiumModal(featureName, event) {
    const permissions = document.getElementById('permissions');
    const hasFollowUserPermission = JSON.parse(permissions.dataset.hasFollowuserPermission);

    if (!hasFollowUserPermission) {
        event.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('followUserModal'));
        modal.show();
        return false;
    }

    return true;
}

function showFollowJourneyPremiumModal(featureName, event) {
    const permissions = document.getElementById('permissions');
    const hasFollowJourneyPermission = JSON.parse(permissions.dataset.hasFollowjourneyPermission);

    if (!hasFollowJourneyPermission) {
        event.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('followJourneyModal'));
        modal.show();
        return false;
    }

    return true;
}