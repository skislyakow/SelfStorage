const button = document.getElementById('copy-utm')

if (button) {
  button.addEventListener('click', () => {
    const field = document.getElementById('utm-result')
    navigator.clipboard.writeText(field.value).then(() => {
      const original = button.textContent
      button.textContent = 'Скопировано'
      setTimeout(() => {
        button.textContent = original
      }, 1500)
    })
  })
}
