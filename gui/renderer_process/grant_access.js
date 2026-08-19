/*
 *   Copyright (c) 2024 Digital Research Alliance of Canada
 *  
 *   This file is part of FRDR Encryption Application.
 *  
 *   FRDR Encryption Application is free software: you can redistribute it
 *   and/or modify it under the terms of the GNU General Public License as
 *   published by the FRDR Encryption Application Software Foundation,
 *   either version 3 of the License, or (at your option) any later version.
 *  
 *   FRDR Encryption Application is distributed in the hope that it will be
 *   useful, but WITHOUT ANY WARRANTY; without even the implied
 *   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *   PURPOSE. See the GNU General Public License for more details.
 *  
 *   You should have received a copy of the GNU General Public License
 *   along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
 */

const {ipcRenderer} = require('electron');

// Request list fetched from API
let pendingRequests = [];
let currentGrantReq = null;

function renderRequestList(requests) {
  const container = $('#request-list');
  container.empty();

  requests.forEach((req) => {
    const datasetTitle = req.title || req.vault_dataset_id;
    const titleDisplay = req.item_uri
      ? `<a href="${req.item_uri}" target="_blank">${datasetTitle}</a>`
      : datasetTitle;
    const requesterDisplay = req.requester_name
      ? `${req.requester_name} (${req.requester_email})`
      : req.requester_email || req.vault_requester_id;

    const card = $(`
      <div class="card mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h5 class="card-title mb-1">${titleDisplay}</h5>
              <p class="mb-0 small text-muted">
                <span data-i18n="app-grant-access-requester"></span>: ${requesterDisplay}
              </p>
              ${req.doi ? `<p class="mb-0 small text-muted"><span data-i18n="app-grant-access-doi"></span>: ${req.doi}</p>` : ''}
              <p class="mb-0 small text-muted">
                <span data-i18n="app-grant-access-request-date"></span> ${req.request_date}
              </p>
            </div>
            <button class="btn btn-primary btn-sm ml-3 grant-access-btn"
                    data-vault-dataset-id="${req.vault_dataset_id}"
                    data-vault-requester-id="${req.vault_requester_id}"
                    data-i18n="app-grant-access-button">
            </button>
          </div>
        </div>
      </div>
    `);

    container.append(card);
  });

  $('[data-i18n]').each(function () {
    $(this).text($.i18n($(this).data('i18n')));
  });
}

function triggerGrantAccess(vaultDatasetId, vaultRequesterId) {
  const req = pendingRequests.find(
    r => r.vault_dataset_id === vaultDatasetId && r.vault_requester_id === vaultRequesterId
  );
  if (!req) return;
  currentGrantReq = req;

  const dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-grant-access-confirm-btn1"), $.i18n("app-grant-access-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-grant-access-confirm")
  };

  ipcRenderer.send("grant-access", req, dialogOptions);
}

function showPleaseWait() {
  if ($('#pleasewaitmodal').length) {
    $('#pleasewaitmodal').modal({ backdrop: 'static', keyboard: false });
  } else {
    console.log("Could not find #pleasewaitmodal div to show please wait modal");
  }
}

function hidePleaseWait() {
  $('#pleasewaitmodal').modal('hide');
}

function disableGrantButton(vaultDatasetId, vaultRequesterId) {
  const btn = $(`.grant-access-btn[data-vault-dataset-id="${vaultDatasetId}"][data-vault-requester-id="${vaultRequesterId}"]`);
  btn.prop('disabled', false);
}

// Load pending requests on page ready
$(function () {
  ipcRenderer.send('get-pending-grant-access-requests');
});

$(function () {
  if ($('#grant-access-done-text').length) {
    const stored = localStorage.getItem('grantedDatasetInfo');
    let datasetDisplay = '';
    if (stored) {
      try {
        const info = JSON.parse(stored);
        datasetDisplay = info.doi ? `${info.title} (${info.doi})` : info.title;
      } catch (e) {}
      localStorage.removeItem('grantedDatasetInfo');
    }
    $('#grant-access-done-text').text($.i18n('app-grant-access-done-text', datasetDisplay));
  }
});

ipcRenderer.on('notify-pending-grant-access-requests', function (_event, requests) {
  $('#loading-state').hide();

  if (!requests || requests.length === 0) {
    $('#empty-state').removeClass("d-none").show();
    return;
  }

  pendingRequests = requests;
  renderRequestList(requests);
  $('#request-list').removeClass("d-none").show();
});

ipcRenderer.on('notify-pending-grant-access-requests-error', function (_event) {
  $('#loading-state').hide();
  $('#error-state').removeClass("d-none").show();
});

$(document).on('click', '.grant-access-btn', function () {
  const vaultDatasetId = $(this).data('vault-dataset-id');
  const vaultRequesterId = $(this).data('vault-requester-id');
  triggerGrantAccess(vaultDatasetId, vaultRequesterId);
});

ipcRenderer.on('notify-grant-access-started', function (_event) {
  showPleaseWait();
});

ipcRenderer.on('notify-grant-access-done', function (_event) {
  hidePleaseWait();
  if (currentGrantReq) {
    localStorage.setItem('grantedDatasetInfo', JSON.stringify({
      title: currentGrantReq.title || currentGrantReq.vault_dataset_id,
      doi: currentGrantReq.doi || null
    }));
  }
  ipcRenderer.send('grant-access-done-show-next-step');
});

ipcRenderer.on('notify-grant-access-error', function (_event, vaultDatasetId, vaultRequesterId, errMessage) {
  const modal = $('#pleasewaitmodal');
  modal.one('hidden.bs.modal', function () {
    disableGrantButton(vaultDatasetId, vaultRequesterId);
    ipcRenderer.send('show-error-dialog', $.i18n('app-grant-access-error', errMessage));
  });
  hidePleaseWait();
});