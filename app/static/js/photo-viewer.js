document.addEventListener('DOMContentLoaded', function() {
    const eventImages = document.querySelectorAll('.event-photo-clickable');
    
    if (eventImages.length > 0) {
        eventImages.forEach(image => {
            image.addEventListener('click', function() {
                const imgSrc = this.getAttribute('src');
                
                const modalImage = document.getElementById('modalImage');
                if (modalImage) {
                    modalImage.setAttribute('src', imgSrc);
                    
                    const photoModal = new bootstrap.Modal(document.getElementById('photoModal'));
                    photoModal.show();
                }
            });
            
            if (!image.hasAttribute('title')) {
                image.setAttribute('title', 'Click to enlarge');
            }
        });
    }
});