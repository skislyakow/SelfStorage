document.getElementById('edit').addEventListener('click', e => {
  e.preventDefault()
  document.getElementById('EMAIL').disabled = false
  document.getElementById('PHONE').disabled = false
  document.getElementById('edit').style.display = 'none'
  document.getElementById('save').style.display = 'inline-block'
})
