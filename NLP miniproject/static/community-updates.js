let updatesList = [];

function renderUpdatesList() {
  let updatesHTML = '';

  for (let i = 0; i < updatesList.length; i++) {
    const update = updatesList[i];
    const { title, description, published } = update;

    const html = `
      <div class="update-item">
        <div>
          <div class="update-title">${title}</div>
          <div class="update-description">${description}</div>
        </div>
        <button class="publish-btn" onclick="publishUpdate(${i})">${published ? 'Unpublish' : 'Publish'}</button>
        <button class="delete-btn" onclick="deleteUpdate(${i})">Delete</button>
      </div>
    `;
    updatesHTML += html;
  }

  document.querySelector('.js-updates-list').innerHTML = updatesHTML;
}

function addUpdate() {
  const titleInput = document.querySelector('.js-title-input');
  const descriptionInput = document.querySelector('.js-description-input');

  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();

  if (title === '' || description === '') {
    alert('Please provide both title and description.');
    return;
  }

  updatesList.push({
    title,
    description,
    published: false
  });

  titleInput.value = '';
  descriptionInput.value = '';

  renderUpdatesList();
}

function deleteUpdate(index) {
  updatesList.splice(index, 1);
  renderUpdatesList();
}

function publishUpdate(index) {
  updatesList[index].published = !updatesList[index].published;
  renderUpdatesList();
}
