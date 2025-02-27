# DRM_add

function doGet(e) {
  try {
    var action = e.parameter.action;
    var ss = SpreadsheetApp.openById("12GNa5BthMjzTI4n-c8Arc_eatCsG0QPwAlDhuq5dglk"); // Ganti dengan ID Spreadsheet yang sesuai
    var sheet = ss.getSheetByName("ALL");

    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Sheet ALL not found" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (action == "get_options") {
      return getOptions(ss);
    } else if (action == "get_data") {
      return getData(sheet);
    } else {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Invalid action" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ "error": error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    var params = JSON.parse(e.postData.contents);
    var action = params.action;
    var ss = SpreadsheetApp.openById("12GNa5BthMjzTI4n-c8Arc_eatCsG0QPwAlDhuq5dglk");
    var sheet = ss.getSheetByName("ALL");

    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Sheet ALL not found" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (action == "add_data") {
      return addData(sheet, params);
    } else {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Invalid action" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ "error": error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getData(sheet) {
  try {
    var data = sheet.getDataRange().getDisplayValues(); // Ambil data sesuai tampilan di Sheets
    var formattedData = [];

    if (data.length < 3) { // Minimal harus ada 3 baris (2 header + 1 data)
      return ContentService.createTextOutput(JSON.stringify({ error: "Data tidak cukup" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var timeZone = Session.getScriptTimeZone(); // Pastikan zona waktu sesuai dengan Apps Script

    for (var i = 2; i < data.length; i++) { // Mulai dari baris ke-3 karena 2 baris pertama adalah header
      var row = data[i].slice();

      // Format Tanggal (misalnya ada di kolom ke-6)
      if (row[5]) { // Pastikan tidak kosong
        var dateValue = new Date(row[5]); // Konversi ke Date jika valid
        if (!isNaN(dateValue.getTime())) {
          row[5] = Utilities.formatDate(dateValue, timeZone, "dd-MMM-yy");
        }
      }

      // Format Waktu Mulai & Selesai (misalnya ada di kolom ke-7 dan ke-8)
      if (row[6]) {
        var startTime = new Date("1970-01-01 " + row[6]); // Pastikan dalam format waktu
        if (!isNaN(startTime.getTime())) {
          row[6] = Utilities.formatDate(startTime, timeZone, "HH:mm");
        }
      }

      if (row[7]) {
        var endTime = new Date("1970-01-01 " + row[7]); // Konversi waktu tanpa tanggal
        if (!isNaN(endTime.getTime())) {
          row[7] = Utilities.formatDate(endTime, timeZone, "HH:mm");
        }
      }

      formattedData.push(row);
    }

    return ContentService.createTextOutput(JSON.stringify(formattedData)).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ "error": error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Ambil opsi untuk select box dari sheet lain
function getOptions(ss) {
  try {
    var sheets = ["BU", "Line", "Produk", "Mesin", "Masalah", "Tindakan Perbaikan", "Deskripsi", "Quantity", "PIC"];
    var options = {};

    sheets.forEach(name => {
      var sheet = ss.getSheetByName(name);
      if (sheet) {
        var values = sheet.getRange("A1:A" + sheet.getLastRow()).getValues().flat().filter(String);
        options[name] = values;
      }
    });

    return ContentService.createTextOutput(JSON.stringify(options)).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ "error": error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Konversi jam ke zona waktu Jakarta
function convertToJakartaTime(timeString) {
  var timeParts = timeString.split(":");
  var date = new Date();
  date.setHours(timeParts[0]);
  date.setMinutes(timeParts[1]);
  date.setSeconds(0);

  return Utilities.formatDate(date, "GMT+7", "HH:mm");
}

// Tambah data ke sheet "ALL"
function addData(sheet, params) {
  try {
    if (!params.Tanggal || !params.Mulai || !params.Selesai) {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Invalid Data" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var lastRow = sheet.getLastRow();
    var newID = 1; // Default jika sheet kosong

    if (lastRow > 1) { // Cek apakah ada data sebelumnya
      var lastID = sheet.getRange(lastRow, 1).getValue(); // Ambil ID dari baris terakhir
      if (!isNaN(lastID) && lastID !== "") {
        newID = lastID + 1; // Tambah 1 dari ID terakhir
      }
    }

    var tanggal = new Date(params.Tanggal);
    var mulai = convertToJakartaTime(params.Mulai);
    var selesai = convertToJakartaTime(params.Selesai);
    var formattedTanggal = Utilities.formatDate(tanggal, "GMT+7", "dd-MMM-yy");

    sheet.appendRow([
      newID, params.BU, params.Line, params.Produk, params.Mesin, formattedTanggal, 
      mulai, selesai, params.Masalah, params.Tindakan, 
      params.Deskripsi, params.Quantity, params.PIC
    ]);

    return ContentService.createTextOutput(JSON.stringify({ "status": "success", "new_id": newID }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ "error": error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
