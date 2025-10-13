document.addEventListener("DOMContentLoaded", function() {
    // Delete single image
    document.querySelectorAll(".delete-single").forEach(btn => {
        btn.addEventListener("click", function() {
            if (confirm("Are you sure you want to delete this single image?")) {
                const url = btn.dataset.url;
                fetch(`/admin/blogs/blog/delete_image/?url=${encodeURIComponent(url)}`)
                    .then(() => location.reload());
            }
        });
    });

    // Delete multiple images
    document.querySelectorAll(".delete-multiple").forEach(btn => {
        btn.addEventListener("click", function() {
            if (confirm("Are you sure you want to delete this image?")) {
                const url = btn.dataset.url;
                fetch(`/admin/blogs/blog/delete_image/?url=${encodeURIComponent(url)}`)
                    .then(() => location.reload());
            }
        });
    });
});
