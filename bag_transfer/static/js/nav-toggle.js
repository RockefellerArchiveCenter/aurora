// Mobile navigation toggle
document.querySelector('#nav-toggle-menu').addEventListener('click', function () {
  this.classList.toggle('active');

  const ariaExpanded = this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true';
  this.setAttribute('aria-expanded', ariaExpanded);
});

document.querySelector('#nav-toggle-menu').addEventListener('click', function () {
  const dropdownItems = document.querySelectorAll('nav .nav__item--dropdown');

  dropdownItems.forEach(function (item) {
    if (item.style.display === 'none' || item.style.display === '') {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
});
