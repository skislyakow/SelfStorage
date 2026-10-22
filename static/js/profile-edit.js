document.getElementById('edit').addEventListener('click', e => {
  e.preventDefault()
  document.getElementById('EMAIL').readOnly = false
  document.getElementById('PHONE').readOnly = false
  e.target.style.display = 'none'
})
