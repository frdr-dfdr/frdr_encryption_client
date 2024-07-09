/*
 *   Copyright (c) 2024 Digital Research Alliance of Canada
 *  
 *   This file is part of FRDR Encryption Application.
 *  
 *   FRDR Encryption Application is free software: you can redistribute it
 *   and/or modify it under the terms of the GNU General Public License as
 *   published by the FRDR Encryption Application Software Foundation,
 *   version 3 of the License.
 *  
 *   FRDR Encryption Application is distributed in the hope that it will be
 *   useful, but WITHOUT ANY WARRANTY; without even the implied
 *   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *   PURPOSE. See the GNU General Public License for more details.
 *  
 *   You should have received a copy of the GNU General Public License
 *   along with Foobar. If not, see <https://www.gnu.org/licenses/>.
 */

const {ipcRenderer} = require("electron");

ipcRenderer.on('notify-send-entity-id-to-frdr-error', function (_event, errMessage) {
  alert($.i18n('app-send-entity-id-to-frdr-error', errMessage), "");
});


ipcRenderer.on('notify-get-entity-id-from-frdr-error', function (_event, errMessage) {
  alert($.i18n('app-get-entity-id-from-frdr-error', errMessage), "");
});