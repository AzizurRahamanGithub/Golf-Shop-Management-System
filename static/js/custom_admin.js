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