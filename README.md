# DRM_add

function doGet(e) {
  try {
    var action = e.parameter.action;
    var ss = SpreadsheetApp.openById("YOUR_SPREADSHEET_ID"); // Replace with actual Spreadsheet ID
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
    var ss = SpreadsheetApp.openById("YOUR_SPREADSHEET_ID");
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
    var data = sheet.getDataRange().getDisplayValues();
    var formattedData = [];

    if (data.length < 3) {
      return ContentService.createTextOutput(JSON.stringify({ error: "Data tidak cukup" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var timeZone = Session.getScriptTimeZone();

    for (var i = 2; i < data.length; i++) {
      var row = data[i].slice();

      if (row[5]) {
        var dateValue = new Date(row[5]);
        if (!isNaN(dateValue.getTime())) {
          row[5] = Utilities.formatDate(dateValue, timeZone, "dd-MMM-yy");
        }
      }

      if (row[6]) {
        var startTime = new Date("1970-01-01 " + row[6]);
        if (!isNaN(startTime.getTime())) {
          row[6] = Utilities.formatDate(startTime, timeZone, "HH:mm");
        }
      }

      if (row[7]) {
        var endTime = new Date("1970-01-01 " + row[7]);
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

function convertToJakartaTime(timeString) {
  var timeParts = timeString.split(":");
  var date = new Date();
  date.setHours(timeParts[0]);
  date.setMinutes(timeParts[1]);
  date.setSeconds(0);

  return Utilities.formatDate(date, "GMT+7", "HH:mm");
}

function addData(sheet, params) {
  try {
    if (!params.Tanggal || !params.Mulai || !params.Selesai) {
      return ContentService.createTextOutput(JSON.stringify({ "error": "Invalid Data" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var lastRow = sheet.getLastRow();
    var newID = 1;

    if (lastRow > 1) {
      var lastID = sheet.getRange(lastRow, 1).getValue();
      if (!isNaN(lastID) && lastID !== "") {
        newID = lastID + 1;
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

