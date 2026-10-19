document.querySelectorAll('[data-wizard-next]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var target = btn.getAttribute('data-wizard-next');
    ['#SignModal', '#RegModal'].forEach(function (sel) {
      var inp = document.querySelector(sel + ' input[name="next"]');
      if (inp) inp.value = target;
    });
  });
});
