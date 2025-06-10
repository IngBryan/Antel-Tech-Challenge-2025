function openFileDialog(i) {
  const fileInput = document.getElementById(`fileInput${i}`);
  if (fileInput) {
    fileInput.click();
  }
}

// Actualiza el nombre del archivo en el input de texto y añade clases para validar
for (let i = 1; i <= 11; i++) {
  const fileInput = document.getElementById(`fileInput${i}`);
  const textInput = document.getElementById(`textInput${i}`);

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      textInput.value = fileInput.files[0].name;
      textInput.classList.remove('is-invalid');
      textInput.classList.add('is-valid');
    } else {
      textInput.value = '';
      textInput.classList.remove('is-valid');
    }
  });
}

document.getElementById('btnEnviar').addEventListener('click', () => {
  const formData = new FormData();
  const fileLabelMap = {};
  let valid = true;

  for (let i = 1; i <= 11; i++) {
    const fileInput = document.getElementById(`fileInput${i}`);
    const textInput = document.getElementById(`textInput${i}`);
    const label = fileInput.dataset.label;

    if (!fileInput.files.length) {
      valid = false;
      textInput.classList.add('is-invalid');
    } else {
      const file = fileInput.files[0];
      formData.append(`file${i}`, file);
      fileLabelMap[`file${i}`] = {
        filename: file.name,
        label: label
      };
      textInput.classList.remove('is-invalid');
      textInput.classList.add('is-valid');
    }
  }

  if (!valid) {
    alert('Por favor, cargá todos los archivos antes de enviar.');
    return;
  }

  // Añadir el objeto que asocia nombres con labels como JSON
  formData.append('fileLabelMap', JSON.stringify(fileLabelMap));

  fetch('/api/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) throw new Error('Error en la carga');
    return response.json();
  })
  .then(data => {
    alert('Archivos cargados con éxito!');
    console.log(data);
  })
  .catch(error => {
    alert('Error al cargar los archivos: ' + error.message);
  });
});
