(function () {
  function toggleAddress() {
    var delivery = document.querySelector('input[name$="delivery_type"]:checked');
    var addr = document.querySelector('input[name$="address"]');
    if (!addr) return;
    var show = !!(delivery && delivery.value !== 'self');
    addr.closest('.mb-3').style.display = show ? '' : 'none';
    addr.required = show;
  }
  document.addEventListener('change', function (e) {
    if (e.target.name && e.target.name.endsWith('delivery_type')) toggleAddress();
  });
  document.addEventListener('DOMContentLoaded', toggleAddress);
})();
