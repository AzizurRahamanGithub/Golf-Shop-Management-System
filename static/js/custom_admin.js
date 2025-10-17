document.addEventListener('DOMContentLoaded', () => {
  console.log('Custom admin JS loaded 😎');
  // Example: Animate sidebar items on hover
  document.querySelectorAll('.sidebar a').forEach(link => {
    link.addEventListener('mouseenter', () => {
      link.style.transform = 'translateX(5px)';
    });
    link.addEventListener('mouseleave', () => {
      link.style.transform = 'translateX(0)';
    });
  });
});



document.querySelectorAll('.field-with-actions').forEach(field => {
    field.style.display = 'flex';
    field.style.alignItems = 'center';
    field.style.gap = '0.5rem';
});


// static/js/custom_admin.js
window.addEventListener('DOMContentLoaded', function() {
    console.log('[custom_admin.js] Connected ✅ — UNFOLD JS loaded');
});
