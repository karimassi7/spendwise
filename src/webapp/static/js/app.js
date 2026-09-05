// SpendWise front-end interactions
(function () {
  // Sidebar toggle for mobile
  var toggleBtn = document.querySelector('.toggle-sidebar');
  var sidebar = document.getElementById('sidebar');

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    var backdrop = document.querySelector('.sidebar-backdrop');
    if (backdrop) backdrop.classList.remove('show');
  }

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      var backdrop = document.querySelector('.sidebar-backdrop');
      if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        backdrop.addEventListener('click', closeSidebar);
        document.body.appendChild(backdrop);
      }
      var open = sidebar.classList.contains('open');
      backdrop.classList.toggle('show', open);
    });
  }

  // Auto-dismiss alerts after a few seconds
  document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      var close = new bootstrap.Alert(alert);
      close.close();
    }, 5000);
  });

  // Bootstrap-style client-side validation for every form
  document.querySelectorAll('form[method="post"]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      if (form.checkValidity()) {
        return true;
      }
      event.preventDefault();
      event.stopPropagation();
      form.classList.add('was-validated');

      var firstInvalid = form.querySelector(':invalid');
      if (firstInvalid) {
        firstInvalid.focus();
      }
      return false;
    }, false);
  });
})();