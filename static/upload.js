const fileListDiv = document.getElementById('fileList');

document.getElementById('fileInput').addEventListener('change', () => {
  const fileInput = document.getElementById('fileInput');

  fileListDiv.innerHTML = ''; // Limpiar lista anterior

  Array.from(fileInput.files).forEach((file, index) => {
    const div = document.createElement('div');
    div.textContent = `${index + 1}. ${file.name}`;
    fileListDiv.appendChild(div);
  });
});

const resultadoDiv = document.getElementById('resultado');

document.getElementById('btnEnviar').addEventListener('click', () => {
  const fileInput = document.getElementById('fileInput');
  const files = fileInput.files;
  const uploadingMessage = document.getElementById('uploadingMessage');
  const btnEnviar = document.getElementById('btnEnviar');

  //if (files.length !== 13) {
  //  alert('Por favor, seleccioná exactamente 13 archivos.');
  //  return;
  //}

  if (files.length == 0) {
    alert('Por favor, seleccioná algún archivo');
    return;
  }

  const formData = new FormData();
  const fileLabelMap = {};

  Array.from(files).forEach((file, i) => {
    const key = `file${i + 1}`;
    formData.append(key, file);
    fileLabelMap[key] = {
      filename: file.name,
      label: `Archivo ${i + 1}`
    };
  });

  formData.append('fileLabelMap', JSON.stringify(fileLabelMap));

  resultadoDiv.textContent = 'Subiendo archivos...';

  fetch('/api/upload', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      if (!response.ok) throw new Error('Error en la carga');
      return response.json();
    })
    .then(data => {
      fileListDiv.innerHTML = '';
      resultadoDiv.textContent = '';
      fileInput.value = '';
      alert('Archivos cargados con éxito!');
      console.log(data);
    })
    .catch(error => {
      alert('Error al cargar los archivos: ' + error.message);
    })
    .finally(() => {
      // Ocultar mensaje y reactivar botón
      uploadingMessage.classList.add('d-none');
      btnEnviar.disabled = false;
    });
});

document.getElementById('btnListar').addEventListener('click', () => {
  resultadoDiv.innerHTML = 'Cargando archivos...';

  fetch('/api/listar-archivos')
    .then(response => {
      if (!response.ok) throw new Error('Error al listar archivos');
      return response.json();
    })
    .then(data => {
      if (data.status === 'ok') {
        if (data.files.length === 0) {
          resultadoDiv.textContent = 'No hay archivos subidos.';
        } else {
          // Crear lista de archivos
          const ul = document.createElement('ul');
          data.files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            ul.appendChild(li);
          });
          resultadoDiv.innerHTML = '<strong>Archivos:</strong>';
          resultadoDiv.appendChild(ul);
        }
      } else {
        resultadoDiv.textContent = 'Error: ' + data.message;
      }
    })
    .catch(error => {
      resultadoDiv.textContent = 'Error: ' + error.message;
    });
});

document.getElementById('btnVaciar').addEventListener('click', () => {
  if (!confirm('¿Seguro que querés vaciar el bucket? Esta acción es irreversible.')) return;

  resultadoDiv.textContent = 'Borrado en proceso...';

  fetch('/api/vaciar-bucket', { method: 'POST' })
    .then(response => {
      if (!response.ok) throw new Error('Error al vaciar bucket');
      return response.json();
    })
    .then(data => {
      if (data.status === 'ok') {
        resultadoDiv.textContent = '';  // Limpio el mensaje previo
        alert('Bucket vaciado correctamente.');
      } else {
        resultadoDiv.textContent = 'Error: ' + data.message;
      }
    })
    .catch(error => {
      resultadoDiv.textContent = 'Error: ' + error.message;
    });
});

document.getElementById('btnReporte').addEventListener('click', () => {
  resultadoDiv.textContent = 'Generando reporte...';

  fetch('/api/generar-reporte', { method: 'POST' })
    .then(response => {
      if (!response.ok) throw new Error('Error al generar el reporte');
      return response.json();
    })
    .then(data => {
      if (data.status === 'ok') {
        resultadoDiv.textContent = '';
        alert('Reporte generado con éxito!');
        console.log(data.resultado);
      } else {
        resultadoDiv.textContent = '';
        alert('Error: ' + data.message);
      }
    })
    .catch(error => {
      alert('Error: ' + error.message);
    });
});