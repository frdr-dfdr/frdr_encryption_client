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
let pendingTransfers = [];

function renderTransferList(transfers) {
  const container = $('#transfer-list');
  container.empty();

  transfers.forEach((req) => {
    const isBulk = req.items.length > 1;
    const datasetTitles = req.items.map(i => {
      const label = i.title || i.vault_dataset_id;
      return i.item_uri
        ? `<li><a href="${i.item_uri}" target="_blank">${label}</a></li>`
        : `<li>${label}</li>`;
    }).join('');

    const firstItem = req.items[0];
    const singleTitle = firstItem.item_uri
      ? `<a href="${firstItem.item_uri}" target="_blank">${firstItem.title || firstItem.vault_dataset_id}</a>`
      : (firstItem.title || firstItem.vault_dataset_id);

    const card = $(`
      <div class="card mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h5 class="card-title mb-1">
                ${isBulk
                  ? $.i18n('app-transfer-ownership-bulk-title', req.items.length)
                  : singleTitle}
              </h5>
              ${isBulk ? `<ul class="mb-2 pl-3 small text-muted">${datasetTitles}</ul>` : ''}
              <p class="mb-1 small text-muted">
                <span data-i18n="app-transfer-ownership-new-owner"></span>: ${req.recipient_email}
              </p>
              <p class="mb-0 small text-muted">
                <span data-i18n="app-transfer-ownership-date"></span>: ${req.request_date}
              </p>
            </div>
            <button class="btn btn-primary btn-sm ml-3 transfer-btn"
                    data-request-id="${req.request_id}"
                    data-i18n="app-transfer-ownership-button">
            </button>
          </div>
        </div>
      </div>
    `);

    container.append(card);
  });

  // Re-apply i18n on newly added elements
  $('[data-i18n]').each(function () {
    $(this).text($.i18n($(this).data('i18n')));
  });
}

function triggerTransfer(requestId) {
  const req = pendingTransfers.find(r => r.request_id === requestId);
  if (!req) return;

  const dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-transfer-ownership-confirm-btn1"), $.i18n("app-transfer-ownership-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-transfer-ownership-confirm")
  };

  // Pass the full request so main process has vault_dataset_id(s) and vault_recipient_id
  ipcRenderer.send("transfer-ownership", req, dialogOptions);
}

function setButtonLoading(requestId) {
  const btn = $(`.transfer-btn[data-request-id="${requestId}"]`);
  btn.prop('disabled', true);
  if ($('#pleasewaitmodal').length) {
    $('#pleasewaitmodal').modal({ backdrop: 'static', keyboard: false });
  } else {
    console.log("Could not find #pleasewaitmodal div to show please wait modal");
  }
}
 
function disableTransferButton(requestId) {
  const btn = $(`.transfer-btn[data-request-id="${requestId}"]`);
  btn.prop('disabled', false);
}
 
// Load pending transfers on page ready
$(function () {
  ipcRenderer.send('get-pending-key-transfers');
});
 
ipcRenderer.on('notify-pending-key-transfers', function (_event, transfers) {
  $('#loading-state').hide();
 
  if (!transfers || transfers.length === 0) {
    $('#empty-state').removeClass("d-none").show();
    return;
  }
 
  pendingTransfers = transfers;
  renderTransferList(transfers);
  $('#transfer-list').removeClass("d-none").show();
});
 
ipcRenderer.on('notify-pending-key-transfers-error', function (_event) {
  $('#loading-state').hide();
  $('#error-state').removeClass("d-none").show();
});
 
$(document).on('click', '.transfer-btn', function () {
  const requestId = parseInt($(this).data('request-id'));
  triggerTransfer(requestId);
});
 
ipcRenderer.on('notify-transfer-ownership-started', function (_event, requestId) {
  setButtonLoading(requestId);
});
 
// IPC responses from main process
ipcRenderer.on('notify-transfer-ownership-done', function (_event) {
  $('#pleasewaitmodal').modal('hide');
  ipcRenderer.send('transfer-ownership-done-show-next-step');
});
 
ipcRenderer.on('notify-transfer-ownership-error', function (_event, requestId, errMessage) {
  const modal = $('#pleasewaitmodal');
  modal.one('hidden.bs.modal', function () {
    disableTransferButton(requestId);
    $('#error-state').text($.i18n('app-transfer-ownership-error', errMessage)).show();
  });
  modal.modal('hide');
});